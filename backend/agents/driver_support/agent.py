"""
Support Agent — with scoped repository.

Uses SupportRepository to ONLY write to coaching_schema tables.
Generates coaching messages for drivers.
"""

import logging
from typing import Any

from agents.base.agent import TDAgentBase
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.support_repo import SupportRepository
from common.models.security import IntentCapsule
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

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

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        capsule = IntentCapsule.model_validate(capsule_data)
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            return result

        await self._update_trip_context_with_support_output(capsule.trip_id, result)
        return result

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate coaching message for driver."""
        try:
            raw = CacheReader.by_key_markers(
                cache_data,
                "trip_context",
                "coaching_history",
                "current_event",
            )
            trip_context = (
                raw["trip_context"] if isinstance(raw["trip_context"], dict) else None
            )
            coaching_history = (
                raw["coaching_history"]
                if isinstance(raw["coaching_history"], list)
                else []
            )
            current_event = (
                raw["current_event"] if isinstance(raw["current_event"], dict) else None
            )
            scoring_snapshot = (
                (trip_context or {}).get("scoring_output") if trip_context else None
            )
            safety_snapshot = (
                (trip_context or {}).get("safety_output") if trip_context else None
            )

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
                coaching_message = f"Coaching for {evt_type}: focus on smooth braking, speed, and follow distance."
                priority = (
                    "high"
                    if str(evt_type).lower() in ("harsh_brake", "collision")
                    else "normal"
                )
            elif scoring_snapshot is not None or safety_snapshot is not None:
                coaching_category = "post_trip"
                score_hint = ""
                if isinstance(scoring_snapshot, dict):
                    s = scoring_snapshot.get("score")
                    if s is not None:
                        score_hint = f" Trip score: {s}."
                coaching_message = (
                    "Post-trip coaching using your score and latest safety summary."
                    + score_hint
                )
                priority = "normal"
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

    async def _update_trip_context_with_support_output(
        self, trip_id: str, support_output: dict[str, Any]
    ) -> None:
        """Persist latest support output summary into trip runtime context."""
        context_key = RedisSchema.Trip.context(trip_id)
        existing = await self._redis.get_trip_context(context_key)
        context = existing if isinstance(existing, dict) else {}
        context["latest_support_output"] = {
            "status": support_output.get("status"),
            "coaching_id": support_output.get("coaching_id"),
            "message": support_output.get("message"),
            "trip_id": support_output.get("trip_id", trip_id),
        }
        context.setdefault("trip_id", trip_id)
        await self._redis.store_trip_context(
            context_key,
            context,
            ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH,
        )
