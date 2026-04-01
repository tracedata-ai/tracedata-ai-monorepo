"""
TraceData Backend — re-exports ORM base and mixins from common.

Implementation: `common.models.sa_base` (avoids circular imports with
`common.models.orm` when `api.models` is loaded).
"""

from common.models.sa_base import Base, TimestampMixin, UUIDPrimaryKeyMixin

__all__ = ["Base", "TimestampMixin", "UUIDPrimaryKeyMixin"]
