from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import PingType, Priority, Source


class CompletionEvent(BaseModel):
    """
    Agent completion event published to Redis.

    When an agent finishes (success or failure),
    it publishes this to the trip's event channel.
    Orchestrator listens and handles accordingly.
    """

    trip_id: str = Field(..., description="Trip ID")
    agent: str = Field(..., description="Agent name (e.g., 'safety', 'scoring')")
    status: str = Field(..., description="'success' or 'failure'")
    completed_at: datetime = Field(default_factory=lambda: datetime.now())
    result: dict[str, Any] = Field(default_factory=dict, description="Agent result")
    error: str | None = Field(None, description="Error message if status='failure'")

    class Config:
        json_schema_extra = {
            "example": {
                "trip_id": "TRIP-123",
                "agent": "safety",
                "status": "success",
                "completed_at": "2024-04-01T12:00:00Z",
                "result": {"decision": "escalate", "severity": 0.95},
            }
        }


class ErrorEvent(BaseModel):
    """
    Agent error event for retry/recovery.

    When an agent fails, this is used to track
    retry attempts and backoff strategy.
    """

    trip_id: str
    device_event_id: str
    agent: str
    error_message: str
    error_type: str
    retry_count: int = 0
    max_retries: int = 3
    next_retry_at: datetime | None = None
    first_error_at: datetime = Field(default_factory=lambda: datetime.now())
    last_error_at: datetime = Field(default_factory=lambda: datetime.now())

    @property
    def can_retry(self) -> bool:
        """Check if we can retry this error."""
        return self.retry_count < self.max_retries

    def next_backoff_seconds(self) -> int:
        """Calculate exponential backoff: 2^retry_count seconds."""
        return 2**self.retry_count


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
    device_event_id: str = Field(..., description="ID stamped by device at detection")
    trip_id: str
    truck_id: str
    driver_id: str
    event_type: str
    category: str
    priority: Priority
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
