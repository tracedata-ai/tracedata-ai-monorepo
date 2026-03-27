"""
TraceData Backend — Fleet (Vehicle/Truck) Model.

Represents a commercial truck in the fleet. Each vehicle belongs to one tenant
and can be assigned to one driver at a time.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    # Only imported during type-checking (not at runtime) — prevents circular imports.
    # SQLAlchemy resolves these forward refs at runtime via its own registry.
    from api.models.driver import Driver
    from api.models.maintenance import Maintenance
    from api.models.trip import Trip


class VehicleStatus(str):
    """
    Allowed statuses for a vehicle
    """

    ACTIVE = "active"
    INACTIVE = "inactive"
    IN_MAINTENANCE = "in_maintenance"


class Vehicle(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Represents a truck / commercial vehicle in the fleet.

    Table: vehicles
    """

    __tablename__ = "vehicles"

    # ── Tenant isolation (MANDATORY) ──────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Tenant this vehicle belongs to. Never query without filtering by this.",
    )

    # ── Vehicle details ────────────────────────────────────────────────────
    license_plate: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment="Vehicle registration plate, e.g. SBA1234A",
    )
    make: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Manufacturer, e.g. Isuzu"
    )
    model: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="Model name, e.g. N-Series"
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    vin: Mapped[str | None] = mapped_column(
        String(17),
        nullable=True,
        unique=True,
        comment="Vehicle Identification Number (optional)",
    )

    # ── Status ─────────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | inactive | in_maintenance",
    )

    # ── Relationships ──────────────────────────────────────────────────────
    # back_populates keeps both sides in sync when you assign vehicle.drivers
    drivers: Mapped[list[Driver]] = relationship("Driver", back_populates="vehicle")
    trips: Mapped[list[Trip]] = relationship("Trip", back_populates="vehicle")
    maintenance_records: Mapped[list[Maintenance]] = relationship(
        "Maintenance", back_populates="vehicle"
    )

    def __repr__(self) -> str:
        return f"<Vehicle {self.license_plate} ({self.status})>"
