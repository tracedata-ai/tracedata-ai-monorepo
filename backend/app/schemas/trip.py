"""TraceData Backend — Trip Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TripCreate(BaseModel):
    """Payload for starting a new trip (Start-of-Trip ping)."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    driver_id: uuid.UUID = Field(..., description="Driver performing this trip")
    vehicle_id: uuid.UUID = Field(..., description="Vehicle used for this trip")
    route_id: uuid.UUID | None = Field(None, description="Pre-defined route, if applicable")
    status: str = Field("active", description="active | completed | zombie")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "driver_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
                "vehicle_id": "a7f3d1c8-2b4e-4f89-9a1d-6e7f8a9b0c1d",
                "route_id": None,
                "status": "active",
            }
        }
    }


class TripRead(TripCreate):
    """
    Schema returned by GET /trips endpoints.

    `safety_score` and `score_explanation` are NULL for active trips.
    They are populated after End-of-Trip scoring by the Behavior Agent.
    """

    id: uuid.UUID
    safety_score: Decimal | None = Field(None, description="XGBoost safety score 0–100")
    score_explanation: str | None = Field(
        None,
        description="SHAP/LIME explanation in JSON format — supports driver transparency",
    )
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
