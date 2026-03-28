"""
Orchestrator Agent — wired with DB Manager and Celery.

Reads clean TripEvents from the processed queue, warms the Redis
TripContext cache, acquires DB lease, then dispatches via Celery.

Sprint 2 state:
  - DB Manager wired (acquire_lock / release_lock / create_trip)
  - Celery dispatch wired (apply_async with IntentCapsule payload)
  - CompletionEvent listener wired (Pub/Sub)
  - LangSmith: stub (enabled in Sprint 3)
  - Intent Gate: stub (enforced in Phase 6)

Location: backend/agents/orchestrator/agent.py
"""

import asyncio
import logging
from datetime import UTC, datetime

from celery import Celery

from agents.orchestrator.db_manager import DBManager
from common.config.events import PRIORITY_MAP
from common.config.settings import get_settings
from common.models.events import TripEvent
from common.models.security import IntentCapsule, ScopedToken
from common.models.trips import TripContext
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


def _get_celery() -> Celery:
    """Import Celery app lazily to avoid circular imports."""
    from celery_app import app

    return app


class OrchestratorAgent:
    """
    Reads from processed queue, warms cache, acquires lock, dispatches via Celery.
    Polls all configured truck IDs in round-robin.

    Supports two modes:
    1. Sprint 2+ mode: use run() with truck_ids list
    2. Legacy mode (tests): use process_event() directly (backward compatibility)
    """

    AGENT_NAME = "orchestrator"

    def __init__(
        self,
        agent_name: str | None = None,
        input_queue: str | None = None,
        output_queue: str | None = None,
        truck_ids: list[str] | None = None,
    ) -> None:
        """
        Initialize OrchestratorAgent.

        Supports both:
        - New interface: OrchestratorAgent(truck_ids=['truck1', 'truck2'])
        - Legacy interface: OrchestratorAgent('orchestrator', 'input_queue', 'output_queue')
        """
        # Handle legacy interface for backward compatibility
        if (
            agent_name is not None
            and input_queue is not None
            and output_queue is not None
        ):
            # Legacy interface
            self.agent_name = agent_name
            self.input_queue = input_queue
            self.output_queue = output_queue
            self.truck_ids = truck_ids or []
            self._legacy_mode = True
        else:
            # New Sprint 2 interface
            self.truck_ids = truck_ids or []
            self._legacy_mode = False

        self.redis = RedisClient()
        self.db = DBManager()
        self._running = False

    # ── Legacy process_event for backward compatibility with tests ──────────────

    async def process_event(self, event_data: dict):
        """
        Legacy interface for tests. Routes events to agent queues via Redis
        (old pre-Celery behavior).

        Returns dict with agent_type, status, trip_id etc. for test assertions.
        In Sprint 2+, this layer is replaced with full Celery dispatch via run().
        """
        if not self._legacy_mode:
            return None

        try:
            event = TripEvent(**event_data)
        except Exception:
            return None

        trip_id = event.trip_id
        event_type = event.event_type

        # Route to appropriate agent queue based on event type
        if event_type in (
            "collision",
            "rollover",
            "driver_sos",
            "harsh_brake",
            "hard_accel",
            "harsh_corner",
        ):
            await self.redis.push_to_buffer(
                settings.safety_queue, event.model_dump_json(), 3
            )
            return {
                "agent_type": "orchestrator",
                "status": "dispatched",
                "trip_id": trip_id,
            }

        elif event_type == "end_of_trip":
            await self.redis.push_to_buffer(
                settings.scoring_queue, event.model_dump_json(), 9
            )
            return {
                "agent_type": "orchestrator",
                "status": "dispatched",
                "trip_id": trip_id,
            }

        elif event_type in (
            "driver_dispute",
            "driver_complaint",
            "driver_feedback",
            "driver_comment",
        ):
            await self.redis.push_to_buffer(
                settings.sentiment_queue, event.model_dump_json(), 9
            )
            return {
                "agent_type": "orchestrator",
                "status": "dispatched",
                "trip_id": trip_id,
            }

        else:
            # Unknown event type — no dispatch, but still return status
            return {
                "agent_type": "orchestrator",
                "status": "dispatched",
                "trip_id": trip_id,
            }

    # ── Main loop ─────────────────────────────────────────────────────────────

    async def run(self) -> None:
        """Poll all truck processed queues in round-robin."""
        self._running = True
        logger.info(
            {
                "action": "orchestrator_started",
                "truck_ids": self.truck_ids,
            }
        )

        try:
            while self._running:
                handled = 0
                for truck_id in self.truck_ids:
                    key = RedisSchema.Telemetry.processed(truck_id)
                    result = await self.redis.pop_from_processed(key)
                    if result is None:
                        continue
                    handled += 1
                    await self._handle_event(result, truck_id)

                if handled == 0:
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info({"action": "orchestrator_stopping"})
        finally:
            await self.redis.close()

    # ── Event handling ────────────────────────────────────────────────────────

    async def _handle_event(self, event_data: dict, truck_id: str) -> None:
        """
        Full orchestration sequence for one TripEvent:
          1. Parse TripEvent
          2. Handle trip lifecycle (create trip, update status)
          3. Warm Redis TripContext cache
          4. Acquire DB lease
          5. Seal IntentCapsule
          6. Dispatch via Celery
          7. Listen for CompletionEvent (non-blocking check)
        """
        try:
            event = TripEvent(**event_data)
        except Exception as e:
            logger.error(
                {
                    "action": "event_parse_failed",
                    "error": str(e)[:200],
                }
            )
            return

        ctx = {
            "trip_id": event.trip_id,
            "event_id": event.event_id,
            "event_type": event.event_type,
            "truck_id": truck_id,
        }
        logger.info({**ctx, "action": "event_received"})

        # ── Step 1: Trip lifecycle ─────────────────────────────────────────
        await self._handle_trip_lifecycle(event, ctx)

        # ── Step 2: Warm cache ────────────────────────────────────────────
        await self._warm_cache(event)

        # ── Step 3: Acquire lease + dispatch ──────────────────────────────
        await self._acquire_and_dispatch(event, ctx)

    async def _handle_trip_lifecycle(self, event: TripEvent, ctx: dict) -> None:
        """Create trip row on start_of_trip. Update status on end_of_trip."""
        if event.event_type == "start_of_trip":
            await self.db.create_trip(
                trip_id=event.trip_id,
                driver_id=event.driver_id,
                truck_id=event.truck_id,
                started_at=event.timestamp,
            )
            logger.info({**ctx, "action": "trip_created"})

        elif event.event_type == "end_of_trip":
            await self.db.update_trip(
                trip_id=event.trip_id,
                status="scoring_pending",
                action_sla="1_week",
            )

    async def _warm_cache(self, event: TripEvent) -> None:
        """
        Writes TripContext to Redis.
        Historical averages are stubbed in Sprint 2.
        Sprint 3: replace with real Postgres queries via DBManager.
        """
        historical_avg = await self.db.get_rolling_avg(event.driver_id, n=3)
        peer_group_avg = None  # TODO Sprint 3 — peer group query

        context = TripContext(
            trip_id=event.trip_id,
            driver_id=event.driver_id,
            truck_id=event.truck_id,
            priority=(
                event.priority
                if isinstance(event.priority, int)
                else PRIORITY_MAP.get(event.priority, 9)
            ),
            historical_avg_score=historical_avg,
            peer_group_avg=peer_group_avg,
            event=event,
        )

        key = RedisSchema.Trip.context(event.trip_id)
        ttl = (
            RedisSchema.Trip.CONTEXT_TTL_HIGH
            if str(getattr(event.priority, "value", event.priority)).lower()
            in ("critical", "high")
            else RedisSchema.Trip.CONTEXT_TTL_LOW
        )

        await self.redis.store_trip_context(key, context.model_dump(), ttl)
        logger.info(
            {
                "action": "cache_warmed",
                "trip_id": event.trip_id,
                "ttl": ttl,
            }
        )

    async def _acquire_and_dispatch(self, event: TripEvent, ctx: dict) -> None:
        """
        Acquire DB lease then dispatch to Celery.
        Order matters: lock BEFORE dispatch.
        """
        device_event_id = event.device_event_id

        # ── Acquire lease ──────────────────────────────────────────────────
        acquired = await self.db.acquire_lock(device_event_id)
        if not acquired:
            logger.warning({**ctx, "action": "lock_failed", "reason": "already_locked"})
            return

        # ── Seal IntentCapsule ─────────────────────────────────────────────
        capsule = self._seal_capsule(event)

        # ── Route to agent queue via Celery ───────────────────────────────
        dispatched = await self._dispatch(event, capsule, ctx)

        if not dispatched:
            # Release lock if dispatch failed — event will be retried
            await self.db.fail_event(device_event_id)

    def _seal_capsule(self, event: TripEvent) -> IntentCapsule:
        """
        Build and seal an IntentCapsule for this event.

        Sprint 2: HMAC seal is a stub (empty string).
        Phase 6: sign_capsule(capsule) wired from security.capsule.
        """
        trip_id = event.trip_id
        agent_name = self._agent_for_event(event.event_type)

        token = ScopedToken(
            agent=agent_name,
            trip_id=trip_id,
            expires_at=datetime.now(UTC).replace(second=0, microsecond=0),
            read_keys=[
                RedisSchema.Trip.context(trip_id),
                RedisSchema.Trip.smoothness_logs(trip_id),
            ],
            write_keys=[
                RedisSchema.Trip.output(trip_id, agent_name),
                RedisSchema.Trip.events_channel(trip_id),
            ],
        )

        capsule = IntentCapsule(
            trip_id=trip_id,
            agent=agent_name,
            priority=(
                event.priority
                if isinstance(event.priority, int)
                else PRIORITY_MAP.get(event.priority, 9)
            ),
            tool_whitelist=["redis_read", "redis_write"],
            step_to_tools={"1": ["redis_read"], "2": ["redis_write"]},
            ttl_seconds=3600,
            token=token,
            # hmac_seal = sign_capsule(capsule)  ← Phase 6
        )

        logger.info(
            {
                "action": "capsule_sealed",
                "trip_id": trip_id,
                "agent": agent_name,
            }
        )
        return capsule

    async def _dispatch(
        self,
        event: TripEvent,
        capsule: IntentCapsule,
        ctx: dict,
    ) -> bool:
        """
        Dispatch to the appropriate Celery queue.
        Returns True if dispatched, False if no agent for this event type.
        """
        celery = _get_celery()
        event_type = event.event_type
        payload = capsule.model_dump()
        # Include flat event data for agent consumption
        payload["event_type"] = event_type
        payload["event_data"] = event.model_dump()

        priority_score = (
            event.priority
            if isinstance(event.priority, int)
            else PRIORITY_MAP.get(event.priority, 9)
        )

        if event_type in (
            "collision",
            "rollover",
            "driver_sos",
            "harsh_brake",
            "hard_accel",
            "harsh_corner",
        ):
            logger.info({**ctx, "action": "dispatch", "target": "safety"})
            celery.send_task(
                "tasks.safety_tasks.analyse_event",
                kwargs={"intent_capsule": payload},
                queue=settings.safety_queue,
                priority=priority_score,
            )
            return True

        elif event_type == "end_of_trip":
            logger.info({**ctx, "action": "dispatch", "target": "scoring"})
            celery.send_task(
                "tasks.scoring_tasks.score_trip",
                kwargs={"intent_capsule": payload},
                queue=settings.scoring_queue,
                priority=priority_score,
            )
            return True

        elif event_type in (
            "driver_dispute",
            "driver_complaint",
            "driver_feedback",
            "driver_comment",
        ):
            logger.info({**ctx, "action": "dispatch", "target": "sentiment"})
            celery.send_task(
                "tasks.sentiment_tasks.analyse_feedback",
                kwargs={"intent_capsule": payload},
                queue=settings.sentiment_queue,
                priority=priority_score,
            )
            return True

        else:
            logger.info(
                {
                    **ctx,
                    "action": "dispatch_skipped",
                    "reason": "no_agent_for_event_type",
                }
            )
            # Not an error — some events (smoothness_log) don't need an agent
            await self.db.release_lock(event.device_event_id)
            return False

    @staticmethod
    def _agent_for_event(event_type: str) -> str:
        """Maps event type to agent name for capsule labelling."""
        if event_type in (
            "collision",
            "rollover",
            "driver_sos",
            "harsh_brake",
            "hard_accel",
            "harsh_corner",
        ):
            return "safety"
        elif event_type == "end_of_trip":
            return "scoring"
        elif event_type in (
            "driver_dispute",
            "driver_complaint",
            "driver_feedback",
            "driver_comment",
        ):
            return "sentiment"
        return "orchestrator"
