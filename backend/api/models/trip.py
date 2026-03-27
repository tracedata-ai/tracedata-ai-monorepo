"""
TraceData Backend — Trip Model.

A trip is the central entity in TraceData. It represents a single journey
made by one driver in one vehicle. It is the key correlation ID used by:
  - The Scoring Agent (to compute the safety score)
  - The Safety Agent (to detect incidents within the trip)
  - The Coaching Agent (to generate feedback post-trip)
  - The Behavior Agent (XGBoost scoring trigger)
"""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Trip(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A single vehicle trip from start to end.

    Status lifecycle:
      active → completed (on End-of-Trip ping)
      active → zombie    (timeout, no End-of-Trip received)

    Table: trips
    """

    __tablename__ = "trips"

    # ── Tenant isolation ────────────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ── Foreign Keys ────────────────────────────────────────────────────────
    driver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="SET NULL"),
        nullable=True,
        comment="Optional: not all trips follow a pre-defined route",
    )

    # ── Trip state ──────────────────────────────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | completed | zombie",
    )

    # ── ML Output ───────────────────────────────────────────────────────────
    # Populated by the Behavior Agent after End-of-Trip scoring
    safety_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
        comment="XGBoost safety score 0–100. NULL until trip is completed and scored.",
    )
    score_explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="SHAP/LIME explanation blob. Stored as JSON string for transparency.",
    )

    # ── Relationships ──────────────────────────────────────────────────────
    driver: Mapped["Driver"] = relationship("Driver", back_populates="trips")  # type: ignore[name-defined] # noqa: F821
    vehicle: Mapped["Vehicle"] = relationship("Vehicle", back_populates="trips")  # type: ignore[name-defined] # noqa: F821
    route: Mapped["Route | None"] = relationship("Route", back_populates="trips")  # type: ignore[name-defined] # noqa: F821
    issues: Mapped[list["Issue"]] = relationship("Issue", back_populates="trip")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return f"<Trip {self.id} driver={self.driver_id} status={self.status} score={self.safety_score}>"
