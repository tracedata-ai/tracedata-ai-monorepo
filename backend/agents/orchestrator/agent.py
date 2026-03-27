import json
import logging

from agents.base.agent import TDAgentBase
from common.config.settings import get_settings
from common.models.events import TripEvent
from common.models.trips import TripContext
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


class OrchestratorAgent(TDAgentBase):
    """
    The Orchestrator dispatch logic.
    Consumes clean TripEvents and dispatches to LangGraph agents.
    """

    async def process_event(self, event_data: dict):
        """
        Step 1: Pull from processed queue (already handled by TDAgentBase.run).
        Step 2: Warm TripContext in Redis.
        Step 3: Route to specific agents.
        """
        try:
            # Reconstruct TripEvent
            event = TripEvent(**event_data)
            settings = get_settings()

            # 1. Warm TripContext in Redis (Role 2 Cache)
            await self._warm_cache_for_trip(event)

            # 2. Dispatch Logic
            if event.event_type == "harsh_brake":
                logger.info(
                    "[trace] orchestrator_dispatch event_id=%s trip_id=%s agent=safety",
                    event.event_id,
                    event.trip_id,
                )
                # For Phase 3, we push to a standard Redis queue.
                # In Sprint 2+, this becomes a Celery apply_async call.
                await self.redis.push_to_buffer(settings.safety_queue, event.model_dump_json(), 3)

            elif event.event_type == "end_of_trip":
                logger.info(
                    "[trace] orchestrator_dispatch event_id=%s trip_id=%s agent=scoring",
                    event.event_id,
                    event.trip_id,
                )
                await self.redis.push_to_buffer(settings.scoring_queue, event.model_dump_json(), 9)

            return {
                "agent_type": "orchestrator",
                "status": "dispatched",
                "trip_id": event.trip_id,
            }

        except Exception as e:
            logger.exception(f"Orchestrator failed to process event: {str(e)}")
            return None

    async def _warm_cache_for_trip(self, event: TripEvent):
        """
        Hydrates Redis with TripContext.
        In a real system, this queries Postgres for historical data.
        """
        # TODO: Query DB Sidecar / Repository for historical averages
        historical_avg = 72.5  # Stub
        peer_group_avg = 68.0  # Stub

        context = TripContext(
            trip_id=event.trip_id,
            driver_id=event.driver_id,  # Already scrubbed by Ingestion Tool
            truck_id=event.truck_id,
            priority=event.priority.value,
            historical_avg_score=historical_avg,
            peer_group_avg=peer_group_avg,
            event=event,
        )

        key = RedisSchema.Trip.context(event.trip_id)
        # Choose TTL based on priority as per 02-0-redis-architecture.md
        ttl = (
            RedisSchema.Trip.CONTEXT_TTL_HIGH
            if event.priority in ["critical", "high"]
            else RedisSchema.Trip.CONTEXT_TTL_LOW
        )

        await self.redis.store_trip_context(key, context.model_dump(), ttl)
        logger.info(f"Warmed cache for trip {event.trip_id} (TTL: {ttl}s)")
