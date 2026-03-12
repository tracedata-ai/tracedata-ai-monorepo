"""
Core Pydantic models for TraceData AI Middleware.

This module contains the base schemas used across the application for 
data validation, serialization, and API responses.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Dict, Any

class TelemetryEventBase(BaseModel):
    """
    Base schema for all telemetry events stored in the system.
    
    This model aligns with the TraceData '4-Ping' lifecycle requirements
    for persistent telemetry storage.
    """
    event_id: str = Field(..., description="Unique ID for this telemetry record")
    event_type: str = Field(..., description="Type of event (start_of_trip, ping, etc.)")
    trip_id: str = Field(..., description="Reference trip identifier")
    driver_id: str = Field(..., description="Reference driver identifier")
    truck_id: Optional[str] = Field(None, description="Reference vehicle identifier")
    timestamp: datetime = Field(..., description="Event generation timestamp")
    location: Optional[Dict[str, float]] = Field(None, description="GPS coordinates {lat, lng}")
    details: Dict[str, Any] = Field(default={}, description="Arbitrary event-specific metadata")

    model_config = ConfigDict(from_attributes=True)

class StandardResponse(BaseModel):
    """
    Universal API response wrapper.
    
    Provides a consistent structure for all middleware responses.
    """
    status: str = Field(..., description="Status indicator (success/error)")
    message: str = Field(..., description="Human-readable summary of the result")
    data: Optional[Dict[str, Any]] = Field(None, description="The actual data payload")
