from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from core.database import Base

class TripScore(Base):
    __tablename__ = "trip_scores"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), nullable=False)
    driver_id = Column(UUID(as_uuid=True), nullable=False)
    
    overall_score = Column(Float) # 0-100
    speeding_penalty = Column(Float)
    harsh_braking_penalty = Column(Float)
    fairness_audit_passed = Column(String(10), default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Reference-only models or just UUIDs for Driver/Trip
