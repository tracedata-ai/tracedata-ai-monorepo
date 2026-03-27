from datetime import datetime

from pydantic import BaseModel


class TripContext(BaseModel):
    trip_id: str
    truck_id: str
    driver_id: str
    status: str
    start_time: datetime
    end_time: datetime | None = None
    distance_km: float = 0.0
