"""
TraceData Backend — Tenant (Fleet Operator) Model.

A tenant represents a fleet operator (company) that owns and manages
vehicles, drivers, and routes. All other entities are linked to a tenant
to ensure data isolation.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Tenant(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A fleet operator / company in the system.

    Table: tenants
    """

    __tablename__ = "tenants"

    # ── Company Details ─────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        unique=True,
        comment="Legal name of the fleet operator company",
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="Primary contact email for the operator",
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
        comment="active | suspended | trial",
    )

    def __repr__(self) -> str:
        return f"<Tenant '{self.name}' ({self.status})>"
