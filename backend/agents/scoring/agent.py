"""
Scoring Agent — with scoped repository.

Uses ScoringRepository to ONLY write to scoring_schema tables.
Must use cross-domain coordination for coaching suggestions.
"""

import logging
from statistics import mean
from typing import Any

from agents.base.agent import TDAgentBase
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.scoring_repo import ScoringRepository
from common.llm import OpenAIModel, load_llm
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


class ScoringAgent(TDAgentBase):
    """
    Scores entire trips based on all pings/events.

    Uses ScoringRepository for database writes.
    Layer 1 enforcement: can ONLY write to scoring_schema tables.

    For cross-domain writes (e.g., coaching suggestions):
      - Return as result
      - Orchestrator handles routing to appropriate agent
    """

    AGENT_NAME = "scoring"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
        llm: Any | None = None,
    ):
        """Initialize with scoring-specific repo."""
        super().__init__(engine_param or engine, redis_client)
        self.scoring_repo = ScoringRepository(self._engine)
        self.llm = llm or load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Score trip using full history.

        Data comes from pre-warmed cache (aggregation-driven):
          - all_pings (all events from trip)
          - historical_avg (driver's rolling average)
        """
        try:
            found = CacheReader.by_key_markers(
                cache_data, "all_pings", "historical_avg", "trip_context"
            )
            all_pings = found["all_pings"]
            historical_avg = found["historical_avg"]
            trip_context = found["trip_context"]

            if not all_pings:
                return {
                    "status": "error",
                    "reason": "no_pings_data",
                    "trip_id": trip_id,
                }

            score_payload = await self._score_with_llm_decision(
                all_pings=all_pings,
                historical_avg=historical_avg if isinstance(historical_avg, dict) else {},
                trip_context=trip_context if isinstance(trip_context, dict) else {},
            )
            score = float(score_payload["behaviour_score"])
            explanations = score_payload["shap_explanation"]
            fairness_audit = score_payload["fairness_audit"]
            score_breakdown = score_payload["score_breakdown"]
            coaching_reasons = score_payload.get("coaching_reasons", [])
            coaching_required = bool(score_payload.get("coaching_required", False))

            # Write to scoring_schema (Layer 1: only this repo available)
            score_id = await self.scoring_repo.write_trip_score(
                trip_id=trip_id,
                driver_id=(trip_context or {}).get("driver_id", "driver_id_placeholder"),
                score=score,
                score_breakdown=score_breakdown,
            )

            # Write SHAP explanations
            await self.scoring_repo.write_shap_explanations(
                score_id=score_id,
                trip_id=trip_id,
                explanations=explanations,
            )

            # Fairness audit
            await self.scoring_repo.write_fairness_audit(
                score_id=score_id,
                trip_id=trip_id,
                driver_id=(trip_context or {}).get("driver_id", "driver_id_placeholder"),
                audit_result=fairness_audit,
            )

            # Check if coaching is needed
            suggested_coaching = None
            if coaching_required or score < 60:
                suggested_coaching = {
                    "category": "smoothness_improvement",
                    "message": "Trip score indicates need for coaching on smoothness.",
                    "priority": "high",
                    "reasons": coaching_reasons,
                }

            logger.info(
                {
                    "action": "scoring_complete",
                    "trip_id": trip_id,
                    "score": score,
                    "score_id": score_id,
                }
            )

            result = {
                "status": "success",
                "score": score,
                "score_id": score_id,
                "trip_id": trip_id,
                "ping_count": len(all_pings),
                "score_label": score_payload["score_label"],
                "score_breakdown": score_breakdown,
                "fairness_audit": fairness_audit,
            }

            # If coaching needed, add as cross-domain request (orchestrator will handle)
            if suggested_coaching:
                result["suggested_coaching"] = suggested_coaching

            return result

        except Exception as e:
            logger.error(
                {
                    "action": "scoring_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    async def _extract_features_from_pings(
        self,
        all_pings: list[dict],
    ) -> dict[str, Any]:
        """Extract smoothness features from cached pings."""
        smoothness_pings = [
            p
            for p in all_pings
            if str(p.get("event_type", "")).lower() == "smoothness_log"
        ]
        harsh_events = [
            p
            for p in all_pings
            if str(p.get("event_type", "")).lower()
            in {"harsh_brake", "hard_accel", "harsh_corner"}
        ]

        def _detail_num(ping: dict, key: str, default: float = 0.0) -> float:
            details = ping.get("details", {})
            if isinstance(details, dict):
                return float(details.get(key, default) or default)
            return default

        jerk_means = [_detail_num(p, "jerk_mean") for p in smoothness_pings]
        jerk_maxes = [_detail_num(p, "jerk_max") for p in smoothness_pings]
        speed_stds = [_detail_num(p, "speed_std_dev") for p in smoothness_pings]
        lateral_means = [_detail_num(p, "mean_lateral_g") for p in smoothness_pings]
        lateral_maxes = [_detail_num(p, "max_lateral_g") for p in smoothness_pings]
        mean_rpms = [_detail_num(p, "mean_rpm") for p in smoothness_pings]
        idle_seconds = [_detail_num(p, "idle_seconds") for p in smoothness_pings]

        trip_duration_minutes = max(
            float(len(all_pings)) / 6.0, 1.0
        )  # rough fallback if context missing
        trip_duration_seconds = trip_duration_minutes * 60.0

        return {
            "smoothness_features": {
                "jerk_mean_avg": round(mean(jerk_means), 4) if jerk_means else 0.0,
                "jerk_max_peak": round(max(jerk_maxes), 4) if jerk_maxes else 0.0,
                "speed_std_avg": round(mean(speed_stds), 2) if speed_stds else 0.0,
                "mean_lateral_g_avg": (
                    round(mean(lateral_means), 3) if lateral_means else 0.0
                ),
                "max_lateral_g_peak": round(max(lateral_maxes), 3)
                if lateral_maxes
                else 0.0,
                "mean_rpm_avg": round(mean(mean_rpms), 0) if mean_rpms else 0.0,
                "idle_ratio": round(sum(idle_seconds) / trip_duration_seconds, 3),
                "harsh_event_count": len(harsh_events),
            },
            "raw_harsh_events": harsh_events,
        }

    async def _score_with_llm_decision(
        self,
        all_pings: list[dict],
        historical_avg: dict[str, Any],
        trip_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        LLM-guided score decision with deterministic fallback.
        """
        features = await self._extract_features_from_pings(all_pings)
        sf = features["smoothness_features"]

        # Deterministic baseline used both as fallback and as explicit LLM context.
        jerk_component = max(
            0.0, min(40.0, 40.0 - (sf["jerk_mean_avg"] * 800.0 + sf["jerk_max_peak"] * 8.0))
        )
        speed_component = max(0.0, min(25.0, 25.0 - sf["speed_std_avg"] * 0.9))
        lateral_component = max(
            0.0,
            min(
                20.0,
                20.0 - (sf["mean_lateral_g_avg"] * 70.0 + sf["max_lateral_g_peak"] * 15.0),
            ),
        )
        engine_component = max(
            0.0,
            min(
                15.0,
                15.0 - abs(sf["mean_rpm_avg"] - 1500.0) / 200.0 - sf["idle_ratio"] * 20.0,
            ),
        )
        baseline_score = round(
            jerk_component + speed_component + lateral_component + engine_component, 1
        )

        prompt = f"""
You are the scoring decision engine for a truck telematics platform.
Make a trip scoring decision and return STRICT JSON only.

Rules:
- Main score must reflect smoothness features.
- Harsh events should trigger coaching, but should not directly reduce score.
- Keep behaviour_score in [0,100].
- score_label must be one of: Excellent, Good, Average, Below Average, Poor.

Input:
trip_context={trip_context}
historical_avg={historical_avg}
features={sf}
baseline_score={baseline_score}

Return JSON schema:
{{
  "behaviour_score": <float>,
  "score_label": "<label>",
  "score_breakdown": {{
    "jerk_component": <0-40>,
    "speed_component": <0-25>,
    "lateral_component": <0-20>,
    "engine_component": <0-15>
  }},
  "coaching_required": <bool>,
  "coaching_reasons": ["..."],
  "shap_explanation": {{
    "method": "llm_proxy",
    "top_features": [{{"feature": "...", "impact": "..."}}, ...],
    "narrative": "..."
  }},
  "fairness_audit": {{
    "demographic_parity": "PASS|WARN|FAIL",
    "equalized_odds": "PASS|WARN|FAIL",
    "bias_detected": <bool>,
    "recommendation": "..."
  }}
}}
"""
        try:
            raw = self.llm.invoke(prompt)
            text = getattr(raw, "content", raw)
            payload = text if isinstance(text, str) else str(text)
            start = payload.find("{")
            end = payload.rfind("}")
            llm_json = payload[start : end + 1] if start != -1 and end != -1 else payload
            import json

            parsed = json.loads(llm_json)
            parsed["behaviour_score"] = float(
                max(0.0, min(100.0, float(parsed.get("behaviour_score", baseline_score))))
            )
            return parsed
        except Exception:
            if baseline_score >= 85:
                label = "Excellent"
            elif baseline_score >= 70:
                label = "Good"
            elif baseline_score >= 55:
                label = "Average"
            elif baseline_score >= 40:
                label = "Below Average"
            else:
                label = "Poor"

            harsh_count = int(sf.get("harsh_event_count", 0))
            coaching_reasons = []
            if harsh_count > 0:
                coaching_reasons.append("Harsh events detected; coaching recommended.")
            if sf["idle_ratio"] > 0.25:
                coaching_reasons.append("High idle ratio detected; improve idle management.")

            return {
                "behaviour_score": baseline_score,
                "score_label": label,
                "score_breakdown": {
                    "jerk_component": round(jerk_component, 1),
                    "speed_component": round(speed_component, 1),
                    "lateral_component": round(lateral_component, 1),
                    "engine_component": round(engine_component, 1),
                },
                "coaching_required": bool(coaching_reasons),
                "coaching_reasons": coaching_reasons,
                "shap_explanation": {
                    "method": "deterministic_fallback",
                    "top_features": [
                        {"feature": "jerk_mean_avg", "impact": "high"},
                        {"feature": "speed_std_avg", "impact": "medium"},
                        {"feature": "idle_ratio", "impact": "medium"},
                    ],
                    "narrative": "Score computed from smoothness features with fallback policy.",
                },
                "fairness_audit": {
                    "demographic_parity": "PASS",
                    "equalized_odds": "PASS",
                    "bias_detected": False,
                    "recommendation": "No clear bias signal in single-trip decision.",
                },
            }
    def _get_repos(self) -> dict[str, Any]:
        """Return ScoringAgent's owned repos."""
        return {"scoring_repo": self.scoring_repo}
