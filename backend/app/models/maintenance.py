"""
TraceData Backend — Maintenance Model.

Tracks the maintenance history and schedule for each vehicle. The Safety Agent
can trigger unscheduled maintenance events (e.g., after a collision detection).
"""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Maintenance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A maintenance record for a vehicle.

    Status lifecycle:
      scheduled → in_progress → completed | overdue

    Table: maintenance
    """

    __tablename__ = "maintenance"

    # ── Tenant isolation ────────────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ── Vehicle FK ──────────────────────────────────────────────────────────
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Maintenance details ─────────────────────────────────────────────────
    maintenance_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="e.g. oil_change | tyre_rotation | brake_inspection | collision_repair",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="scheduled",
        comment="scheduled | in_progress | completed | overdue",
    )
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Free-text notes from the mechanic or fleet manager",
    )

    # ── Trigger context ─────────────────────────────────────────────────────
    triggered_by: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="manual",
        comment="manual | safety_agent | schedule — tracks what caused this record",
    )

    # ── Relationships ──────────────────────────────────────────────────────
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="maintenance_records")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return (
            f"<Maintenance {self.maintenance_type} vehicle={self.vehicle_id} status={self.status}>"
        )
