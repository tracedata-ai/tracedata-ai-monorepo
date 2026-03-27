"""TraceData Backend — Issue Pydantic Schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class IssueCreate(BaseModel):
    """Payload for logging a driving issue/event."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    trip_id: uuid.UUID = Field(..., description="Trip this issue occurred in")
    severity: str = Field(..., description="critical | high | medium | low")
    category: str = Field(
        ...,
        description="harsh_events | speed_compliance | critical | idle_fuel | normal_operation",
    )
    event_type: str = Field(
        ...,
        description="e.g. harsh_brake | speeding | collision | excessive_idle",
    )
    description: str | None = Field(None, description="Optional human-readable context")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "trip_id": "b2e4c6a8-1d3f-5e7g-9h1j-k2l4m6n8o0p2",
                "severity": "high",
                "category": "harsh_events",
                "event_type": "harsh_brake",
                "description": "Hard braking at 80 km/h on PIE near Toa Payoh exit",
            }
        }
    }


class IssueRead(IssueCreate):
    """Schema returned by GET /issues endpoints."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
