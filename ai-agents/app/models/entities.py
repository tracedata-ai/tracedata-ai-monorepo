"""
SQLAlchemy ORM models for core entities in the TraceData AI Middleware.
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base

class Fleet(Base):
    __tablename__ = "fleet"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vin = Column(String(17), unique=True, nullable=False)
    license_plate = Column(String(20), unique=True, nullable=False)
    make = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    year = Column(String(4), nullable=False)
    status = Column(String(20), default="active") # active, maintenance, retired
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="vehicle")
    issues = relationship("Issue", back_populates="vehicle")

class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    status = Column(String(20), default="active") # active, suspended, inactive
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="driver")

class Route(Base):
    __tablename__ = "routes"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    start_location = Column(String(255), nullable=False)
    end_location = Column(String(255), nullable=False)
    estimated_distance = Column(Float) # in km
    estimated_duration = Column(Float) # in hours
    created_at = Column(DateTime, default=datetime.utcnow)

    trips = relationship("Trip", back_populates="route")

class Trip(Base):
    __tablename__ = "trips"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.fleet.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.drivers.id"), nullable=False)
    route_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.routes.id"), nullable=False)
    
    status = Column(String(20), default="scheduled") # scheduled, in_progress, completed, cancelled
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    actual_distance = Column(Float)
    safety_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Fleet", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    route = relationship("Route", back_populates="trips")
    issues = relationship("Issue", back_populates="trip")

class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.fleet.id"), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.trips.id"), nullable=True)
    
    issue_type = Column(String(50), nullable=False) # mechanical, safety, telemetry, other
    severity = Column(String(20), default="low") # low, medium, high, critical
    description = Column(Text)
    status = Column(String(20), default="open") # open, investigating, resolved, closed
    reported_at = Column(DateTime, default=datetime.utcnow)

    vehicle = relationship("Fleet", back_populates="issues")
    trip = relationship("Trip", back_populates="issues")

class SentimentRecord(Base):
    __tablename__ = "sentiment_records"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.drivers.id"), nullable=False)
    risk_level = Column(Float) # 0 to 1
    sentiment_score = Column(Float) # -1 to 1
    raw_text = Column(Text)
    reported_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver")

class Appeal(Base):
    __tablename__ = "appeals"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.drivers.id"), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.trips.id"), nullable=False)
    
    reason = Column(Text, nullable=False)
    status = Column(String(20), default="open") # open, investigating, approved, rejected
    ai_reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver")
    trip = relationship("Trip")

class CoachingRecord(Base):
    __tablename__ = "coaching_records"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.drivers.id"), nullable=False)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.trips.id"), nullable=False)
    
    coaching_text = Column(Text, nullable=False)
    tone = Column(String(20)) # Encouraging, Supportive, Directive
    created_at = Column(DateTime, default=datetime.utcnow)

    driver = relationship("Driver")
    trip = relationship("Trip")

class TelemetryEvent(Base):
    """
    Flat Schema Telemetry as per SRS Section 3.1 & 3.2.
    """
    __tablename__ = "telemetry_events"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.trips.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.fleet.id"), nullable=False)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("fleet_schema.drivers.id"), nullable=False)
    
    event_type = Column(String(50), nullable=False) # collision, harsh_brake, etc.
    category = Column(String(50)) # critical, harsh_event, etc.
    priority = Column(String(20)) # critical, high, medium, low
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    latitude = Column(Float)
    longitude = Column(Float)
    
    # event-specific fields flattened into JSONB for XAI/Fairness audits
    details = Column(Text) # Storing as text but could be JSONB if Postgres version supports it well in this setup

    trip = relationship("Trip")
    vehicle = relationship("Fleet")
    driver = relationship("Driver")
