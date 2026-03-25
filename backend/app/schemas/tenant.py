"""
TraceData Backend — Tenant Schemas.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TenantBase(BaseModel):
    """Shared fields for Tenant."""

    name: str
    contact_email: str | None = None
    status: str = "active"


class TenantCreate(TenantBase):
    """Schema for creating a Tenant."""

    pass


class TenantRead(TenantBase):
    """Schema for reading a Tenant."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
