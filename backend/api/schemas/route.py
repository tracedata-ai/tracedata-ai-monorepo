"""TraceData Backend — Route Pydantic Schemas."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class RouteCreate(BaseModel):
    """Payload for creating a new route."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    name: str = Field(..., max_length=200, description="e.g. 'Tuas Hub → Tampines Hub'")
    start_location: str = Field(..., max_length=300)
    end_location: str = Field(..., max_length=300)
    distance_km: Decimal | None = Field(None, description="Distance in kilometres")
    route_type: str = Field(
        "highway",
        description="highway | urban | mixed — informs context-aware safety scoring",
    )
    start_lat: float | None = None
    start_lon: float | None = None
    end_lat: float | None = None
    end_lon: float | None = None
    waypoints: list[dict] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Tuas Hub \u2192 Tampines Distribution Centre",
                "start_location": "Tuas Hub, 51 Gul Circle, Singapore 629586",
                "end_location": "Tampines Distribution Centre, 3 Tampines Industrial Ave, Singapore 528798",
                "distance_km": "42.5",
                "route_type": "highway",
            }
        }
    }


class RouteRead(RouteCreate):
    """Schema returned by GET /routes endpoints."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
