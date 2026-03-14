from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class DriverBase(BaseModel):
    first_name: str
    last_name: str
    license_number: str
    email: Optional[str] = None
    status: str = "active"

class DriverSchema(DriverBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DriverList(BaseModel):
    items: List[DriverSchema]
    total: int

class CoachingBase(BaseModel):
    driver_id: UUID
    trip_id: UUID
    coaching_text: str
    tone: str

class CoachingSchema(CoachingBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
