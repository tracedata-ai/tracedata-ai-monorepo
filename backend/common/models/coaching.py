from pydantic import BaseModel
from typing import List

class CoachingResult(BaseModel):
    trip_id: str
    tips: List[str]
    priority: int
