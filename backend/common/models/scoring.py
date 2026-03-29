from typing import Any

from pydantic import BaseModel


class ScoringResult(BaseModel):
    trip_id: str
    behaviour_score: float
    smoothness_score: float
    shap_values: dict[str, float]
    fairness_result: dict[str, Any]
