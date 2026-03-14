from sqlalchemy import Column, String, Float, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from core.database import Base

class Fleet(Base):
    __tablename__ = "fleet"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vin = Column(String(17), unique=True, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(String(4), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class Route(Base):
    __tablename__ = "routes"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    estimated_distance = Column(Float)
    estimated_duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False) # Reference by UUID
    driver_id = Column(UUID(as_uuid=True), nullable=False)  # Reference by UUID
    route_id = Column(UUID(as_uuid=True), nullable=False)   # Reference by UUID
    
    status = Column(String(20), default="scheduled")
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    actual_distance = Column(Float)
    safety_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    trip_id = Column(UUID(as_uuid=True), nullable=True)
    
    issue_type = Column(String(50), nullable=False)
    severity = Column(String(20), default="low")
    description = Column(Text)
    status = Column(String(20), default="open")
    reported_at = Column(DateTime, default=datetime.utcnow)

class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=False)
    
    event_type = Column(String(50), nullable=False)
    category = Column(String(50))
    priority = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    latitude = Column(Float)
    longitude = Column(Float)
    details = Column(Text)
