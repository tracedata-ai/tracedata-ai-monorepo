"""
Support Agent — with scoped repository.

Uses SupportRepository to ONLY write to coaching_schema tables.
Generates coaching messages for drivers.
"""

import logging
from typing import Any

from common.db.engine import engine
from common.db.repositories.support_repo import SupportRepository
from common.redis.client import RedisClient
from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SupportAgent(TDAgentBase):
    """Generates coaching messages for drivers."""

    AGENT_NAME = "support"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
    ):
        """Initialize with support-specific repo."""
        super().__init__(engine_param or engine, redis_client)
        self.support_repo = SupportRepository(self._engine)

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate coaching message for driver."""
        try:
            trip_context: dict[str, Any] | None = None
            coaching_history: list[Any] | None = None
            current_event: dict[str, Any] | None = None

            for key, value in cache_data.items():
                if "trip_context" in key:
                    trip_context = value if isinstance(value, dict) else None
                elif "coaching_history" in key:
                    coaching_history = value if isinstance(value, list) else []
                elif "current_event" in key:
                    current_event = value if isinstance(value, dict) else None

            driver_id = (
                (trip_context or {}).get("driver_id", "driver_id_placeholder")
                if trip_context
                else "driver_id_placeholder"
            )

            history_n = len(coaching_history or [])
            if history_n > 0:
                coaching_category = "follow_up"
                coaching_message = (
                    f"Continuing coaching — {history_n} prior notes on this trip. "
                    "Keep applying prior guidance and drive safely."
                )
                priority = "normal"
            elif current_event:
                coaching_category = "event_based"
                evt_type = current_event.get("event_type", "event")
                coaching_message = (
                    f"Coaching for {evt_type}: focus on smooth braking, speed, and follow distance."
                )
                priority = "high" if str(evt_type).lower() in ("harsh_brake", "collision") else "normal"
            else:
                coaching_category = "general"
                coaching_message = "Keep safe driving practices!"
                priority = "normal"

            # Write to coaching_schema (Layer 1: only this repo available)
            coaching_id = await self.support_repo.write_coaching(
                trip_id=trip_id,
                driver_id=driver_id,
                coaching_category=coaching_category,
                message=coaching_message,
                priority=priority,
            )

            logger.info(
                {
                    "action": "coaching_generated",
                    "trip_id": trip_id,
                    "coaching_id": coaching_id,
                }
            )

            return {
                "status": "success",
                "coaching_id": coaching_id,
                "message": coaching_message,
                "trip_id": trip_id,
            }

        except Exception as e:
            logger.error(
                {
                    "action": "coaching_generation_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    def _get_repos(self) -> dict[str, Any]:
        """Return SupportAgent's owned repos."""
        return {"support_repo": self.support_repo}
