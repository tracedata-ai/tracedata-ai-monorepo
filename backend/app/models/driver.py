"""
TraceData Backend — Driver Model.

A driver is a person who operates vehicles. Each driver belongs to one tenant,
may be assigned to one vehicle, and generates trips + feedback over time.
"""

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Driver(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A truck driver registered in the system.

    Table: drivers
    """

    __tablename__ = "drivers"

    # ── Tenant isolation (MANDATORY) ──────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ── Personal details ────────────────────────────────────────────────────
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    license_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Driver's commercial vehicle license number",
    )

    # ── Status & Classification ─────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | inactive | suspended",
    )
    experience_level: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="novice",
        comment="novice | intermediate | expert — used for fairness cohorts in AIF360",
    )

    # ── Foreign Key — assigned vehicle (optional) ────────────────────────────
    vehicle_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        comment="Currently assigned vehicle. NULL if not assigned.",
    )

    # ── Relationships ──────────────────────────────────────────────────────
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="drivers")  # type: ignore[name-defined] # noqa: F821
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="driver")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return f"<Driver {self.first_name} {self.last_name} [{self.experience_level}]>"
