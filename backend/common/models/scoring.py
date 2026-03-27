from pydantic import BaseModel
from typing import Dict, Any

class ScoringResult(BaseModel):
    trip_id: str
    behaviour_score: float
    smoothness_score: float
    shap_values: Dict[str, float]
    fairness_result: Dict[str, Any]
