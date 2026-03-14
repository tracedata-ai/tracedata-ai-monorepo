from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class TripScoreBase(BaseModel):
    trip_id: UUID
    driver_id: UUID
    overall_score: float
    fairness_audit_passed: str = "pending"

class TripScoreSchema(TripScoreBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
