"""TraceData Backend — Driver Pydantic Schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class DriverCreate(BaseModel):
    """Payload for registering a new driver."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)
    email: str = Field(..., description="Driver's email address")
    phone: str | None = Field(None, max_length=20)
    license_number: str = Field(
        ..., max_length=50, description="Commercial vehicle license number"
    )
    status: str = Field("active", description="active | inactive | suspended")
    experience_level: str = Field(
        "novice",
        description="novice | intermediate | expert — used for AIF360 fairness cohort assignment",
    )
    vehicle_id: uuid.UUID | None = Field(
        None, description="Assigned vehicle. NULL if unassigned."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "first_name": "Ravi",
                "last_name": "Kumar",
                "email": "ravi.kumar@fleet.sg",
                "phone": "+65 9123 4567",
                "license_number": "SG-CDL-2019-00421",
                "status": "active",
                "experience_level": "intermediate",
                "vehicle_id": None,
            }
        }
    }


class DriverRead(DriverCreate):
    """Schema returned by GET /drivers endpoints."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
