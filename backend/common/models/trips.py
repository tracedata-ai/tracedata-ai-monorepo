from pydantic import BaseModel

from .events import TripEvent


class TripContext(BaseModel):
    """
    Shared context for a specific trip.
    Warmed once by Orchestrator, read by all agents.
    """

    trip_id: str
    driver_id: str  # Anonymized to DRV-ANON-XXXX
    truck_id: str
    priority: int
    historical_avg_score: float | None = None
    peer_group_avg: float | None = None
    event: TripEvent
