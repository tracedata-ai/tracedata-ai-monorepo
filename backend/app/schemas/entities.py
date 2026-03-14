"""
Pydantic schemas for validation and serialization of core entities.
"""

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# --- Base Schemas ---

class FleetBase(BaseModel):
    vin: str = Field(..., min_length=17, max_length=17)
    license_plate: str
    make: str
    model: str
    year: str
    status: str = "active"

class DriverBase(BaseModel):
    first_name: str
    last_name: str
    license_number: str
    phone: Optional[str] = None
    email: Optional[str] = None
    status: str = "active"

class RouteBase(BaseModel):
    name: str
    start_location: str
    end_location: str
    estimated_distance: Optional[float] = None
    estimated_duration: Optional[float] = None

class TripBase(BaseModel):
    vehicle_id: UUID
    driver_id: UUID
    route_id: UUID
    status: str = "scheduled"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    actual_distance: Optional[float] = None
    safety_score: Optional[float] = None

class IssueBase(BaseModel):
    vehicle_id: UUID
    trip_id: Optional[UUID] = None
    issue_type: str
    severity: str = "low"
    description: Optional[str] = None
    status: str = "open"

# --- Response Schemas (include IDs and timestamps) ---

class FleetSchema(FleetBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DriverSchema(DriverBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RouteSchema(RouteBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TripSchema(TripBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IssueSchema(IssueBase):
    id: UUID
    reported_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- List Response Schemas ---

class FleetList(BaseModel):
    items: List[FleetSchema]
    total: int

class DriverList(BaseModel):
    items: List[DriverSchema]
    total: int

class RouteList(BaseModel):
    items: List[RouteSchema]
    total: int

class TripList(BaseModel):
    items: List[TripSchema]
    total: int

class IssueList(BaseModel):
    items: List[IssueSchema]
    total: int

# --- New AI Agent Schemas ---

class SentimentBase(BaseModel):
    driver_id: UUID
    risk_level: float
    sentiment_score: float
    raw_text: Optional[str] = None

class SentimentSchema(SentimentBase):
    id: UUID
    reported_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AppealBase(BaseModel):
    driver_id: UUID
    trip_id: UUID
    reason: str
    status: str = "open"
    ai_reasoning: Optional[str] = None

class AppealSchema(AppealBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CoachingBase(BaseModel):
    driver_id: UUID
    trip_id: UUID
    coaching_text: str
    tone: str

class CoachingSchema(CoachingBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TelemetryBase(BaseModel):
    trip_id: UUID
    vehicle_id: UUID
    driver_id: UUID
    event_type: str
    category: Optional[str] = None
    priority: Optional[str] = None
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    details: Optional[str] = None

class TelemetrySchema(TelemetryBase):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
# --- API Payloads ---

class TelemetryPayload(BaseModel):
    """
    Schema for incoming telemetry data from vehicles.
    """
    event_id: str = Field(..., description="Universally unique identifier for the event")
    event_type: str = Field(..., description="The kind of event (e.g., end_of_trip, harsh_brake)")
    trip_id: str = Field(..., description="Identifier for the current active trip")
    driver_id: str = Field(..., description="Identifier for the driver generating the event")
    timestamp: str = Field(..., description="ISO8601 UTC timestamp of the event")
    details: dict = Field(default={}, description="Type-specific dynamic fields")

class ChatPayload(BaseModel):
    """Schema for direct chat interactions with the agentic middleware."""
    message: str = Field(..., description="The user's message to the agent")
