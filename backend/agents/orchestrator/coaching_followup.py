"""
Post-scoring coaching handoff.

After Scoring succeeds on end_of_trip, enqueue coaching_ready onto the truck
processed queue so Support runs in a second wave with scoring + safety outputs.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncEngine

from common.config.events import EVENT_MATRIX, PRIORITY_MAP, processed_queue_sort_score
from common.db.repositories.events_repo import EventsRepo
from common.db.repositories.trips_repo import TripsRepo
from common.models.enums import Priority, Source
from common.models.events import TripEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


async def schedule_coaching_ready_if_pending(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
) -> None:
    try:
        await _schedule_coaching_ready_if_pending_impl(
            redis=redis, engine=engine, trip_id=trip_id
        )
    except Exception:
        logger.exception(
            {"action": "coaching_ready_enqueue_failed", "trip_id": trip_id}
        )


async def _schedule_coaching_ready_if_pending_impl(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
) -> None:
    ctx_key = RedisSchema.Trip.context(trip_id)
    raw = await redis._client.get(ctx_key)
    if not raw:
        return
    try:
        context = json.loads(raw)
    except json.JSONDecodeError:
        return
    if not isinstance(context, dict) or not context.get(
        "coaching_pending_after_scoring"
    ):
        return

    trips_repo = TripsRepo(engine)
    ids = await trips_repo.get_truck_and_driver(trip_id)
    truck_id = context.get("truck_id")
    driver_id = context.get("driver_id")
    if ids:
        truck_id = truck_id or ids[0]
        driver_id = driver_id or ids[1]
    if not truck_id or not driver_id:
        logger.warning(
            {
                "action": "coaching_ready_skipped_no_ids",
                "trip_id": trip_id,
            }
        )
        return

    cfg = EVENT_MATRIX["coaching_ready"]
    event_id = str(uuid.uuid4())
    device_event_id = f"cr-{uuid.uuid4().hex[:12]}"

    events_repo = EventsRepo(engine)
    inserted = await events_repo.insert_synthetic_received_event(
        device_event_id=device_event_id,
        event_id=event_id,
        trip_id=trip_id,
        truck_id=str(truck_id),
        driver_id=str(driver_id),
        event_type="coaching_ready",
        category=cfg.category,
        priority=cfg.priority.value,
        timestamp=datetime.now(UTC),
        details={"followup": "post_scoring_coaching"},
    )
    if not inserted:
        logger.warning(
            {
                "action": "coaching_ready_insert_skipped",
                "trip_id": trip_id,
                "device_event_id": device_event_id,
            }
        )
        return

    ev = TripEvent(
        event_id=event_id,
        device_event_id=device_event_id,
        trip_id=trip_id,
        truck_id=str(truck_id),
        driver_id=str(driver_id),
        event_type="coaching_ready",
        category=cfg.category,
        priority=Priority(str(cfg.priority.value)),
        timestamp=datetime.now(UTC),
        offset_seconds=0,
        source=Source.SYSTEM,
    )
    payload = ev.model_dump_json()
    proc_key = RedisSchema.Telemetry.processed(str(truck_id))
    tier = PRIORITY_MAP.get(str(cfg.priority.value), 6)
    score = processed_queue_sort_score(ev.timestamp, tier)
    await redis.push_to_processed(proc_key, payload, score=score)

    context["coaching_pending_after_scoring"] = False
    await redis.store_trip_context(
        ctx_key, context, ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH
    )

    logger.info(
        {
            "action": "coaching_ready_enqueued",
            "trip_id": trip_id,
            "device_event_id": device_event_id,
            "truck_id": truck_id,
        }
    )
