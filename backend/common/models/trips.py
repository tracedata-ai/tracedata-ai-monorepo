from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TripContext(BaseModel):
    trip_id: str
    truck_id: str
    driver_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    distance_km: float = 0.0
