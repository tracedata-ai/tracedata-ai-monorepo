from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, Optional

class TripEvent(BaseModel):
    event_id: str = Field(..., description="Globally unique UUID")
    device_event_id: str = Field(..., description="ID stamped by device at detection")
    trip_id: str
    truck_id: str
    driver_id: str
    event_type: str
    category: Optional[str] = None
    priority: Optional[str] = None
    timestamp: datetime
    offset_seconds: int
    trip_meter_km: float
    odometer_km: float
    location: Optional[Dict[str, float]] = None
    schema_version: str = "event_v1"
    details: Dict[str, Any] = Field(default_factory=dict)

class TelemetryPacket(BaseModel):
    batch_id: Optional[str] = None
    ping_type: str
    source: str
    is_emergency: bool = False
    event: TripEvent
    evidence: Optional[Dict[str, Any]] = None
