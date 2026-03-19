"""
TraceData Backend — ORM Base Class & Shared Mixins.

All SQLAlchemy models inherit from `Base`. The `TimestampMixin` automatically
adds `created_at` and `updated_at` columns to every table — zero boilerplate.

Pattern: Declarative Base (SQLAlchemy 2.0 style).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    The single Declarative Base for all ORM models.

    SQLAlchemy uses this to discover and manage all tables.
    When we call `Base.metadata.create_all(engine)` in main.py,
    it creates every table that inherits from this class.
    """
    pass


class TimestampMixin:
    """
    Mixin that adds `created_at` and `updated_at` to any model.

    `server_default=func.now()` means PostgreSQL sets the value,
    not Python — this avoids timezone confusion.
    `onupdate=func.now()` automatically updates on every row change.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDPrimaryKeyMixin:
    """
    Mixin that adds a UUID primary key column named `id`.

    Using UUIDs instead of auto-incrementing integers because:
    - Multi-tenant safe (no sequential ID guessing)
    - Can be generated client-side or server-side
    - Globally unique across services
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
