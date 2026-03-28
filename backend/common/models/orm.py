import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class EventORM(Base):
    """
    Every telemetry event that passes through the Ingestion Tool.
    Written by:  Ingestion Tool (DB WRITE 1, status=received)
    Updated by:  DB Manager (status transitions, lock lifecycle)
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(36), unique=True)
    device_event_id: Mapped[str] = mapped_column(String(50), unique=True)
    trip_id: Mapped[str] = mapped_column(String(100))
    truck_id: Mapped[str] = mapped_column(String(50))
    driver_id: Mapped[str] = mapped_column(String(50))  # REAL ID — audit only
    event_type: Mapped[str] = mapped_column(String(50))
    category: Mapped[str] = mapped_column(String(50))
    priority: Mapped[str] = mapped_column(String(20))
    ping_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source: Mapped[str | None] = mapped_column(String(30), nullable=True)
    is_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    offset_seconds: Mapped[int] = mapped_column(Integer)
    trip_meter_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    odometer_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Lease-based locking ───────────────────────────────────────────────────
    # status = 'processing' → agent running (watchdog eligible after lock_ttl)
    # status = 'locked'     → HITL in progress (watchdog NEVER resets this)
    status: Mapped[str] = mapped_column(String(20), default="received")
    locked_by: Mapped[str | None] = mapped_column(String(50), nullable=True)
    locked_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    processed_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    ingested_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )


class TripORM(Base):
    """
    One row per trip. Tracks the full trip lifecycle state machine.

    Status machine:
      active           → trip in progress, events still arriving
      scoring_pending  → end_of_trip received, Scoring Agent dispatched
      coaching_pending → score computed, DSP dispatched
      complete         → all agents done, mission closed
      failed           → agent error after max retries
      locked           → HITL in progress — watchdog NEVER resets this

    Written by:  DB Manager (via Orchestrator)
    Read by:     Orchestrator, Scoring Agent (rolling average query)
    """

    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    trip_id: Mapped[str] = mapped_column(String(100), unique=True)
    driver_id: Mapped[str] = mapped_column(String(50))  # anonymised DRV-ANON-XXXX
    truck_id: Mapped[str] = mapped_column(String(50))

    # Temporal
    started_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    ended_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Route summary
    distance_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    route_type: Mapped[str | None] = mapped_column(String(30), nullable=True)

    # Trip lifecycle — see status machine above
    status: Mapped[str] = mapped_column(String(30), default="active")
    action_sla: Mapped[str | None] = mapped_column(String(20), nullable=True)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)

    # Mission closure
    capsule_closed: Mapped[bool] = mapped_column(Boolean, default=False)
    closed_at: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
