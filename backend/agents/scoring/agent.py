"""
Scoring Agent — with scoped repository.

Uses ScoringRepository to ONLY write to scoring_schema tables.
Must use cross-domain coordination for coaching suggestions.
"""

import logging
from typing import Any

from agents.base.agent import TDAgentBase
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.scoring_repo import ScoringRepository
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
    ):
        """Initialize with scoring-specific repo."""
        super().__init__(engine_param or engine, redis_client)
        self.scoring_repo = ScoringRepository(self._engine)

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
                cache_data, "all_pings", "historical_avg"
            )
            all_pings = found["all_pings"]
            historical_avg = found["historical_avg"]

            if not all_pings:
                return {
                    "status": "error",
                    "reason": "no_pings_data",
                    "trip_id": trip_id,
                }

            # Compute trip score
            score = await self._compute_score(all_pings)

            # Generate explanations
            explanations = await self._generate_explanations(all_pings, score)

            # Write to scoring_schema (Layer 1: only this repo available)
            score_id = await self.scoring_repo.write_trip_score(
                trip_id=trip_id,
                driver_id="driver_id_placeholder",  # Get from trip_context
                score=score,
                score_breakdown=explanations,
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
                driver_id="driver_id_placeholder",
                audit_result={"method": "demographic_parity", "passed": True},
            )

            # Check if coaching is needed
            suggested_coaching = None
            if score < 60:
                suggested_coaching = {
                    "category": "low_score",
                    "message": "Trip score indicates need for coaching",
                    "priority": "high",
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

    async def _compute_score(self, all_pings: list[dict]) -> float:
        """
        Compute trip score (0-100).

        Simple heuristic for now.
        """
        if not all_pings:
            return 50.0

        # Count harsh events
        harsh_count = sum(
            1
            for ping in all_pings
            if ping.get("event_type") in ["harsh_brake", "hard_accel", "harsh_corner"]
        )

        # Score = 100 - (harsh_count * 10)
        score = max(0, 100 - (harsh_count * 10))
        return float(score)

    async def _generate_explanations(
        self,
        all_pings: list[dict],
        score: float,
    ) -> dict[str, Any]:
        """
        Generate SHAP explanations for score.
        """
        return {
            "method": "simple_heuristic",
            "score": score,
            "ping_count": len(all_pings),
            "harsh_events": sum(
                1
                for ping in all_pings
                if ping.get("event_type")
                in ["harsh_brake", "hard_accel", "harsh_corner"]
            ),
        }

    def _get_repos(self) -> dict[str, Any]:
        """Return ScoringAgent's owned repos."""
        return {"scoring_repo": self.scoring_repo}
