from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from core.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    license_number = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20))
    email = Column(String(100), unique=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class CoachingSession(Base):
    __tablename__ = "coaching_records"
    __table_args__ = {"schema": "fleet_schema"}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    driver_id = Column(UUID(as_uuid=True), nullable=False)
    trip_id = Column(UUID(as_uuid=True), nullable=False)
    
    coaching_text = Column(Text, nullable=False)
    tone = Column(String(20))
    sentiment_score = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
