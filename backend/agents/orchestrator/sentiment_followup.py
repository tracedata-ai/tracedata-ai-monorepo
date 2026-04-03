"""
Post-sentiment support handoff.

After Sentiment succeeds on driver feedback, enqueue sentiment_ready onto the
truck processed queue so Orchestrator can run Support with sentiment output.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncEngine

from common.config.events import EVENT_MATRIX, PRIORITY_MAP
from common.db.repositories.events_repo import EventsRepo
from common.db.repositories.trips_repo import TripsRepo
from common.models.enums import Priority, Source
from common.models.events import TripEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


async def schedule_sentiment_ready_if_success(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
) -> None:
    try:
        await _schedule_sentiment_ready_if_success_impl(
            redis=redis, engine=engine, trip_id=trip_id
        )
    except Exception:
        logger.exception(
            {"action": "sentiment_ready_enqueue_failed", "trip_id": trip_id}
        )


async def _schedule_sentiment_ready_if_success_impl(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
) -> None:
    sentiment_output_key = RedisSchema.Trip.output(trip_id, "sentiment")
    sentiment_raw = await redis._client.get(sentiment_output_key)
    if not sentiment_raw:
        return
    try:
        sentiment_output = json.loads(sentiment_raw)
    except json.JSONDecodeError:
        return
    if (
        not isinstance(sentiment_output, dict)
        or sentiment_output.get("status") != "success"
    ):
        return

    ctx_key = RedisSchema.Trip.context(trip_id)
    raw_ctx = await redis._client.get(ctx_key)
    context: dict = {}
    if raw_ctx:
        try:
            parsed_ctx = json.loads(raw_ctx)
            if isinstance(parsed_ctx, dict):
                context = parsed_ctx
        except json.JSONDecodeError:
            context = {}
    if context.get("sentiment_support_pending"):
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
                "action": "sentiment_ready_skipped_no_ids",
                "trip_id": trip_id,
            }
        )
        return

    cfg = EVENT_MATRIX["sentiment_ready"]
    event_id = str(uuid.uuid4())
    device_event_id = f"sr-{uuid.uuid4().hex[:12]}"

    events_repo = EventsRepo(engine)
    inserted = await events_repo.insert_synthetic_received_event(
        device_event_id=device_event_id,
        event_id=event_id,
        trip_id=trip_id,
        truck_id=str(truck_id),
        driver_id=str(driver_id),
        event_type="sentiment_ready",
        category=cfg.category,
        priority=cfg.priority.value,
        timestamp=datetime.now(UTC),
        details={"followup": "post_sentiment_support"},
    )
    if not inserted:
        logger.warning(
            {
                "action": "sentiment_ready_insert_skipped",
                "trip_id": trip_id,
                "device_event_id": device_event_id,
            }
        )
        return

    event = TripEvent(
        event_id=event_id,
        device_event_id=device_event_id,
        trip_id=trip_id,
        truck_id=str(truck_id),
        driver_id=str(driver_id),
        event_type="sentiment_ready",
        category=cfg.category,
        priority=Priority(str(cfg.priority.value)),
        timestamp=datetime.now(UTC),
        offset_seconds=0,
        source=Source.SYSTEM,
    )
    proc_key = RedisSchema.Telemetry.processed(str(truck_id))
    score = PRIORITY_MAP.get(cfg.priority.value, 6)
    await redis.push_to_processed(proc_key, event.model_dump_json(), score=score)

    context["sentiment_support_pending"] = True
    context.setdefault("trip_id", trip_id)
    context.setdefault("driver_id", str(driver_id))
    context.setdefault("truck_id", str(truck_id))
    await redis.store_trip_context(
        ctx_key, context, ttl=RedisSchema.Trip.CONTEXT_TTL_HIGH
    )

    logger.info(
        {
            "action": "sentiment_ready_enqueued",
            "trip_id": trip_id,
            "device_event_id": device_event_id,
            "truck_id": truck_id,
        }
    )
