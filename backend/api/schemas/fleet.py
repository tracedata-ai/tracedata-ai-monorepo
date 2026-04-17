"""
TraceData Backend — Fleet (Vehicle) Pydantic Schemas.

Pydantic v2 schemas are the contract between the API and its clients.
They define what JSON goes IN (create/update) and what JSON comes OUT (read).

Separation of schemas (Read vs Create) is intentional:
  - `VehicleRead`   — what the API returns (includes id, timestamps)
  - `VehicleCreate` — what the client POSTs (no id/timestamps needed)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class VehicleCreate(BaseModel):
    """Payload for creating a new vehicle. Client sends this."""

    tenant_id: uuid.UUID = Field(..., description="Owning tenant UUID")
    license_plate: str = Field(..., max_length=20, description="e.g. SBA1234A")
    make: str = Field(..., max_length=50, description="Manufacturer name")
    model: str = Field(..., max_length=50, description="Model name")
    year: int = Field(..., ge=1990, le=2100, description="Manufacturing year")
    vin: str | None = Field(
        None, max_length=17, description="Vehicle Identification Number"
    )
    status: str = Field("active", description="active | inactive | in_maintenance")
    fuel_level: int = Field(100, ge=0, le=100, description="Fuel level percentage 0-100")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tenant_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "license_plate": "SBA1234A",
                "make": "Isuzu",
                "model": "N-Series NMR85H",
                "year": 2022,
                "vin": "JNKBANT15Z0000001",
                "status": "active",
            }
        }
    }


class VehicleRead(VehicleCreate):
    """
    Schema returned by GET endpoints.

    Extends VehicleCreate and adds server-generated fields.
    `model_config = {"from_attributes": True}` tells Pydantic to read from
    SQLAlchemy ORM objects (not just plain dicts).
    """

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    has_open_maintenance: bool = False

    model_config = {"from_attributes": True}
