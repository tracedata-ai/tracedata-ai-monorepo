"""
TraceData Backend — Route Model.

A route defines a named path between two locations. It provides the geographic
context used by the Context Enrichment Agent when scoring trips.
"""

import uuid
from decimal import Decimal

from sqlalchemy import Float, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Route(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A named delivery route between two points.

    Table: routes
    """

    __tablename__ = "routes"

    # ── Tenant isolation ────────────────────────────────────────────────────
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    # ── Route details ───────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Human-readable route name, e.g. 'Tuas Hub → Tampines Hub'",
    )
    start_location: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        comment="Start address or zone name",
    )
    end_location: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        comment="End address or zone name",
    )
    distance_km: Mapped[Decimal | None] = mapped_column(
        Numeric(7, 2),
        nullable=True,
        comment="Approximate route distance in kilometres",
    )
    route_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="highway",
        comment="highway | urban | mixed — used for context-aware scoring",
    )
    start_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_lon: Mapped[float | None] = mapped_column(Float, nullable=True)
    waypoints: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        comment='Intermediate waypoints: [{"lat": 1.33, "lon": 103.72, "name": "Jurong East"}, ...]',
    )

    # ── Relationships ──────────────────────────────────────────────────────
    trips: Mapped[list["Trip"]] = relationship("Trip", back_populates="route")  # type: ignore[name-defined] # noqa: F821

    def __repr__(self) -> str:
        return f"<Route '{self.name}' ({self.distance_km} km)>"
