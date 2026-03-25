"""
TraceData Backend — Issue Model.

An issue is a specific driving event captured within a trip (e.g., harsh brake,
speeding). Issues are classified by severity and category, and they feed into
the safety score and coaching recommendations.
"""

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Issue(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A classified driving event within a trip.

    Severity levels align with the 4-priority Redis topic routing:
      critical → emergency_channel
      high     → safety_channel
      medium   → general_events
      low      → analytics

    Table: issues
    """

    __tablename__ = "issues"

    # ── Tenant isolation ────────────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ── Parent trip ─────────────────────────────────────────────────────────
    trip_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Every issue must belong to exactly one trip.",
    )

    # ── Classification ──────────────────────────────────────────────────────
    severity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="critical | high | medium | low",
    )
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="harsh_events | speed_compliance | critical | idle_fuel | normal_operation",
    )
    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="e.g. harsh_brake, speeding, collision, excessive_idle",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Human-readable description of the event, optionally enriched by an agent",
    )

    # ── Relationships ──────────────────────────────────────────────────────
    trip: Mapped["Trip"] = relationship("Trip", back_populates="issues")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return f"<Issue {self.event_type} severity={self.severity} trip={self.trip_id}>"
