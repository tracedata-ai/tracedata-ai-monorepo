from pydantic import BaseModel


class EmergencySignal(BaseModel):
    trip_id: str
    severity: str
    dispatch_required: bool
