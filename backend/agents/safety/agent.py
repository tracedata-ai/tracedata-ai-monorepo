"""
Safety Agent — with scoped repository.

Uses SafetyRepository to ONLY write to safety_schema tables.
Layer 1 enforcement: repo injection makes it impossible to write elsewhere.
"""

import logging
from typing import Any

from common.db.engine import engine
from common.db.repositories.safety_repo import SafetyRepository
from common.redis.client import RedisClient
from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SafetyAgent(TDAgentBase):
    """
    Analyzes safety-critical events (collisions, harsh braking, etc).

    Uses SafetyRepository for database writes.
    Layer 1 enforcement: can ONLY write to safety_schema tables.
    """

    AGENT_NAME = "safety"

    def __init__(
        self,
        engine=None,
        redis_client: RedisClient | None = None,
    ):
        """Initialize with safety-specific repo."""
        super().__init__(engine or engine, redis_client)
        self.safety_repo = SafetyRepository(self._engine)

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Analyze safety event.

        Data comes from pre-warmed cache (no DB queries during analysis!):
          - current_event (1-2 KB from event-driven warming)
          - trip_context (1-2 KB)
        """
        try:
            # Extract from cache
            current_event = None
            trip_context = None

            for key, value in cache_data.items():
                if "current_event" in key:
                    current_event = value
                elif "trip_context" in key:
                    trip_context = value

            if not current_event:
                return {
                    "status": "error",
                    "reason": "no_event_data",
                    "trip_id": trip_id,
                }

            # Analyze severity
            severity = await self._assess_severity(current_event)

            # Determine action
            action = await self._determine_action(severity)

            # Write to safety_schema (Layer 1: only this repo available)
            decision_id = await self.safety_repo.write_safety_decision(
                event_id=current_event.get("event_id"),
                trip_id=trip_id,
                decision="escalate" if severity >= 0.9 else "monitor",
                action=action,
                reason=f"Severity: {severity:.2f}",
            )

            # Also write analysis
            await self.safety_repo.write_harsh_event_analysis(
                event_id=current_event.get("event_id"),
                trip_id=trip_id,
                event_type=current_event.get("event_type"),
                severity=current_event.get("severity", "unknown"),
                analysis={
                    "assessed_severity": severity,
                    "trip_context": trip_context,
                    "recommended_action": action,
                },
            )

            logger.info(
                {
                    "action": "safety_analysis_complete",
                    "trip_id": trip_id,
                    "severity": severity,
                    "decision_id": decision_id,
                }
            )

            return {
                "status": "success",
                "severity": severity,
                "action": action,
                "decision_id": decision_id,
                "trip_id": trip_id,
            }

        except Exception as e:
            logger.error(
                {
                    "action": "safety_analysis_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    async def _assess_severity(self, event_data: dict) -> float:
        """
        Assess severity of safety event.

        Returns:
            0.0-1.0 severity score
        """
        # Simple heuristic for now
        severity_map = event_data.get("severity", "medium")
        return {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}.get(
            severity_map, 0.5
        )

    async def _determine_action(self, severity: float) -> str:
        """
        Determine action based on severity.

        Returns:
            Action string (e.g., "emergency_alert", "coaching")
        """
        if severity >= 0.9:
            return "emergency_alert"
        elif severity >= 0.7:
            return "coaching"
        else:
            return "monitoring"

    def _get_repos(self) -> dict[str, Any]:
        """Return SafetyAgent's owned repos."""
        return {"safety_repo": self.safety_repo}
