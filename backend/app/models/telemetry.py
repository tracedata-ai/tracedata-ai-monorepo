"""
TelemetryRaw — one row per Kafka message from the truck simulator.

DESIGN: Append-only event log.
    Never UPDATE or DELETE rows. This table is the raw source of truth.
    Downstream agents (Driver Behavior, Maintenance) read from here.

FIELD SOURCES (from master_plan.md simulated data spec):
    vehicle_id, driver_id, driver_age, timestamp, speed, engine_temp,
    oil_pressure, brake_wear_index, harsh_braking_count,
    rapid_acceleration_count, cornering_force, shift_type, GPS coords

VECTOR(2) for location:
    Stores [longitude, latitude] as a pgvector VECTOR type.
    This enables ANN (approximate nearest neighbour) queries later —
    e.g. "find the 5 nearest depots to this breakdown location".
    Plain FLOAT columns would work for display; VECTOR works for that
    AND for semantic geo queries with no extra cost today.

JSONB payload:
    The full original Kafka message is stored here so we never lose data.
    If we need a field we didn't think to extract today, it's in payload.
    This is the "landing zone" pattern — extract what you need now,
    leave the rest queryable.

TRACE EXERCISE:
    Simulator publishes a Kafka message for Vehicle V007 / Driver D023.
    Trace what happens:
    1. Kafka consumer receives the message
    2. Consumer deserialises JSON → creates TelemetryRaw instance
    3. db.add(row) → session stages the row (not yet in Postgres)
    4. get_db() commits → row written to telemetry_raw
    5. Which agent reads this row next?
"""

import enum
import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ShiftType(str, enum.Enum):
    DAY   = "day"
    NIGHT = "night"


class TelemetryRaw(Base):
    __tablename__ = "telemetry_raw"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Foreign references (UUID only — no DB-level FK across bounded contexts)
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True
    )
    driver_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )

    # ── Demographics (denormalised for query performance + bias analysis) ──────
    # Storing driver_age here avoids a JOIN when the Orchestrator computes
    # aggregate risk scores per age group across millions of telemetry rows.
    driver_age: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── Timing ────────────────────────────────────────────────────────────────
    event_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True,
        comment="When the event occurred on the vehicle (device clock)"
    )
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        comment="When the backend received this event (server clock)"
    )

    # ── Location ──────────────────────────────────────────────────────────────
    # [longitude, latitude] stored as VECTOR(2) for ANN geo queries
    location: Mapped[list[float] | None] = mapped_column(
        Vector(2), nullable=True,
        comment="[longitude, latitude] — VECTOR(2) enables pgvector ANN queries"
    )

    # ── Telemetry Scalars (agreed simulator fields) ───────────────────────────
    speed_kmh: Mapped[float | None]              = mapped_column(Float, nullable=True)
    engine_temp_c: Mapped[float | None]          = mapped_column(Float, nullable=True)
    oil_pressure_kpa: Mapped[float | None]        = mapped_column(Float, nullable=True)
    brake_wear_index: Mapped[float | None]        = mapped_column(Float, nullable=True,
        comment="0.0 (new) to 1.0 (worn out) — triggers Maintenance Agent alert at > 0.8")
    harsh_braking_count: Mapped[int | None]       = mapped_column(Integer, nullable=True,
        comment="Key bias feature: young drivers +35% vs senior at equivalent speed")
    rapid_acceleration_count: Mapped[int | None]  = mapped_column(Integer, nullable=True)
    cornering_force_g: Mapped[float | None]       = mapped_column(Float, nullable=True)
    shift_type: Mapped[ShiftType | None]          = mapped_column(
        Enum(ShiftType, name="shift_type_enum"), nullable=True,
        comment="day | night — night shifts correlate with fatigue incidents"
    )

    # ── Full Kafka Payload (source of truth) ──────────────────────────────────
    payload: Mapped[dict] = mapped_column(
        JSONB, nullable=False, default=dict,
        comment="Complete original Kafka message — never lose fields we forgot to extract"
    )

    # ── Kafka Metadata (for replay / debugging) ───────────────────────────────
    kafka_topic: Mapped[str | None]     = mapped_column(String(255), nullable=True)
    kafka_partition: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kafka_offset: Mapped[int | None]    = mapped_column(Integer, nullable=True)

    # ── Index: most common query — latest events for a vehicle ────────────────
    __table_args__ = (
        Index(
            "ix_telemetry_vehicle_ts",
            "vehicle_id", "event_timestamp",
        ),
    )

    def __repr__(self) -> str:
        return f"<TelemetryRaw vehicle={self.vehicle_id} ts={self.event_timestamp}>"
