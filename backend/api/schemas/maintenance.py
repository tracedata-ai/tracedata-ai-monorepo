"""TraceData Backend — Maintenance Pydantic Schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class MaintenanceCreate(BaseModel):
    """Payload for creating a maintenance record."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    vehicle_id: uuid.UUID = Field(..., description="Vehicle requiring maintenance")
    maintenance_type: str = Field(
        ...,
        max_length=100,
        description="e.g. oil_change | tyre_rotation | brake_inspection | collision_repair",
    )
    status: str = Field(
        "scheduled", description="scheduled | in_progress | completed | overdue"
    )
    scheduled_date: date | None = Field(None)
    completed_date: date | None = Field(None)
    notes: str | None = Field(None)
    triggered_by: str = Field(
        "manual",
        description="manual | safety_agent | schedule — full traceability of who created this record",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "vehicle_id": "a7f3d1c8-2b4e-4f89-9a1d-6e7f8a9b0c1d",
                "maintenance_type": "brake_inspection",
                "status": "scheduled",
                "scheduled_date": "2026-04-01",
                "completed_date": None,
                "notes": "Post-collision inspection triggered by Safety Agent alert",
                "triggered_by": "safety_agent",
            }
        }
    }


class MaintenanceRead(MaintenanceCreate):
    """Schema returned by GET /maintenance endpoints."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
