from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

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

class TelemetryPayload(BaseModel):
    event_id: str = Field(..., description="Universally unique identifier for the event")
    event_type: str = Field(..., description="The kind of event (e.g., end_of_trip, harsh_brake)")
    trip_id: str = Field(..., description="Identifier for the current active trip")
    driver_id: str = Field(..., description="Identifier for the driver generating the event")
    timestamp: str = Field(..., description="ISO8601 UTC timestamp of the event")
    details: dict = Field(default={}, description="Type-specific dynamic fields")

class FleetSchema(BaseModel):
    id: UUID
    vin: str
    license_plate: str
    make: str
    model: str
    year: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class FleetList(BaseModel):
    items: List[FleetSchema]
    total: int

class RouteSchema(BaseModel):
    id: UUID
    name: str
    start_location: str
    end_location: str
    estimated_distance: float
    estimated_duration: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RouteList(BaseModel):
    items: List[RouteSchema]
    total: int

class TripSchema(BaseModel):
    id: UUID
    vehicle_id: UUID
    driver_id: UUID
    route_id: UUID
    status: str
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    actual_distance: Optional[float]
    safety_score: Optional[float]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class TripList(BaseModel):
    items: List[TripSchema]
    total: int

class IssueSchema(BaseModel):
    id: UUID
    vehicle_id: UUID
    trip_id: Optional[UUID]
    issue_type: str
    severity: str
    description: Optional[str]
    status: str
    reported_at: datetime
    model_config = ConfigDict(from_attributes=True)

class IssueList(BaseModel):
    items: List[IssueSchema]
    total: int
