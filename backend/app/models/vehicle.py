"""
Vehicle — a fleet vehicle that generates telemetry.

FLEET SIZE (from master_plan.md):
    50 vehicles: V001–V050
    Varied manufacture years: 2015–2023
    Vehicle IDs in simulator match this table's primary keys.

VIN uniqueness:
    Vehicle Identification Number is globally unique (17 chars, ISO 3779).
    We enforce this at the DB level (UNIQUE constraint) — not just in app code.
    App-level validation alone can be bypassed by concurrent inserts.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class VehicleType(str, enum.Enum):
    TRUCK = "truck"
    VAN   = "van"
    CAR   = "car"


class VehicleStatus(str, enum.Enum):
    AVAILABLE   = "available"
    IN_USE      = "in_use"
    MAINTENANCE = "maintenance"
    RETIRED     = "retired"


class Vehicle(Base):
    __tablename__ = "vehicles"

    # ── Identity ──────────────────────────────────────────────────────────────
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # ── Registration ──────────────────────────────────────────────────────────
    vin: Mapped[str] = mapped_column(
        String(17), nullable=False, unique=True, index=True,
        comment="Vehicle Identification Number — 17 chars, globally unique (ISO 3779)"
    )
    plate_number: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )

    # ── Attributes ────────────────────────────────────────────────────────────
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(
        Integer, nullable=False,
        comment="Manufacture year — range 2015–2023 per simulator spec"
    )
    vehicle_type: Mapped[VehicleType] = mapped_column(
        Enum(VehicleType, name="vehicle_type_enum"),
        nullable=False, default=VehicleType.TRUCK
    )

    # ── Operational Status ────────────────────────────────────────────────────
    status: Mapped[VehicleStatus] = mapped_column(
        Enum(VehicleStatus, name="vehicle_status_enum"),
        nullable=False, default=VehicleStatus.AVAILABLE
    )

    # ── Timestamps ────────────────────────────────────────────────────────────
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self) -> str:
        return f"<Vehicle {self.plate_number} ({self.make} {self.model} {self.year})>"
