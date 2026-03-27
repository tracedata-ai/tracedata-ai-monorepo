
from pydantic import BaseModel


class CoachingResult(BaseModel):
    trip_id: str
    tips: list[str]
    priority: int
