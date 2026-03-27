from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import PingType, Priority, Source


class Location(BaseModel):
    lat: float
    lon: float


class Evidence(BaseModel):
    video_url: str | None = None
    voice_url: str | None = None
    sensor_dump_url: str | None = None
    video_duration_seconds: int | None = None
    capture_offset_seconds: int | None = None


class TripEvent(BaseModel):
    event_id: str = Field(..., description="Globally unique UUID")
    device_event_id: str = Field(
        ..., description="ID stamped by device at detection"
    )
    trip_id: str
    truck_id: str
    driver_id: str
    event_type: str
    category: str
    priority: Priority | int
    timestamp: datetime
    offset_seconds: int
    trip_meter_km: float | None = None
    odometer_km: float | None = None
    location: Location | None = None
    schema_version: str = "event_v1"
    details: dict[str, Any] = Field(default_factory=dict)
    
    # Processed metadata added after ingestion
    evidence: Evidence | None = None
    source: Source | None = None
    ping_type: PingType | None = None
    is_emergency: bool | None = None
    ingested_at: datetime | None = None



class TelemetryPacket(BaseModel):
    batch_id: str | None = None
    ping_type: PingType
    source: Source
    is_emergency: bool = False
    event: TripEvent
    evidence: Evidence | None = None
