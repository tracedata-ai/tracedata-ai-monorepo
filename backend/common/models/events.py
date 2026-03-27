from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TripEvent(BaseModel):
    event_id: str = Field(..., description="Globally unique UUID")
    device_event_id: str = Field(..., description="ID stamped by device at detection")
    trip_id: str
    truck_id: str
    driver_id: str
    event_type: str
    category: str | None = None
    priority: str | None = None
    timestamp: datetime
    offset_seconds: int
    trip_meter_km: float
    odometer_km: float
    location: dict[str, float] | None = None
    schema_version: str = "event_v1"
    details: dict[str, Any] = Field(default_factory=dict)


class TelemetryPacket(BaseModel):
    batch_id: str | None = None
    ping_type: str
    source: str
    is_emergency: bool = False
    event: TripEvent
    evidence: dict[str, Any] | None = None
