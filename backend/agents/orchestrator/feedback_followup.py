"""
Post-scoring driver feedback injection.

After Scoring completes, auto-inject a synthetic driver_feedback event whose
sentiment style is paired to the trip score so the dataset is realistic:

  score >= 80  →  "excellent"  (5-star pool)
  score >= 70  →  "good"       (4-star pool)
  score >= 60  →  "average"    (3-star pool)
  score  < 60  →  "poor"       (1-2-star pool)

Skips injection when a driver_feedback event already exists for the trip.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from common.config.events import EVENT_MATRIX, PRIORITY_MAP, processed_queue_sort_score
from common.db.repositories.events_repo import EventsRepo
from common.db.repositories.trips_repo import TripsRepo
from common.models.enums import Priority, Source
from common.models.events import TripEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


def _style_from_score(score: float) -> str:
    if score >= 80:
        return "excellent"
    if score >= 70:
        return "good"
    if score >= 60:
        return "average"
    return "poor"


async def inject_driver_feedback_if_absent(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
    score: float,
) -> None:
    try:
        await _inject_impl(redis=redis, engine=engine, trip_id=trip_id, score=score)
    except Exception:
        logger.exception({"action": "feedback_inject_failed", "trip_id": trip_id})


async def _inject_impl(
    *,
    redis: RedisClient,
    engine: AsyncEngine,
    trip_id: str,
    score: float,
) -> None:
    # Check if feedback already exists for this trip
    async with engine.begin() as conn:
        row = await conn.execute(
            text(
                "SELECT 1 FROM pipeline_events "
                "WHERE trip_id = :trip_id AND event_type = 'driver_feedback' "
                "LIMIT 1"
            ),
            {"trip_id": trip_id},
        )
        if row.first() is not None:
            logger.info(
                {"action": "feedback_inject_skipped_exists", "trip_id": trip_id}
            )
            return

    trips_repo = TripsRepo(engine)
    ids = await trips_repo.get_truck_and_driver(trip_id)
    if not ids:
        logger.warning({"action": "feedback_inject_skipped_no_ids", "trip_id": trip_id})
        return
    truck_id, driver_id = str(ids[0]), str(ids[1])

    style = _style_from_score(score)

    # Build feedback details using the same pool logic as driver_feedback_packet()
    import random as _rnd

    from common.workflow_fixtures.mock_driver_feedback import FEEDBACK_POOL as _POOL

    if style in {"excellent", "good"}:
        pool = [e for e in _POOL if e[1] >= 4]
    elif style == "average":
        pool = [e for e in _POOL if e[1] == 3]
    else:
        pool = [e for e in _POOL if e[1] <= 2]
    message, rating, fatigue = _rnd.choice(pool or list(_POOL))

    cfg = EVENT_MATRIX["driver_feedback"]
    event_id = str(uuid.uuid4())
    device_event_id = f"fb-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)

    events_repo = EventsRepo(engine)
    inserted = await events_repo.insert_synthetic_received_event(
        device_event_id=device_event_id,
        event_id=event_id,
        trip_id=trip_id,
        truck_id=truck_id,
        driver_id=driver_id,
        event_type="driver_feedback",
        category=cfg.category,
        priority=cfg.priority.value,
        timestamp=now,
        details={
            "trip_rating": rating,
            "message": message,
            "fatigue_self_report": fatigue,
            "synthetic": True,
            "score_style": style,
        },
    )
    if not inserted:
        logger.warning(
            {
                "action": "feedback_insert_skipped",
                "trip_id": trip_id,
                "device_event_id": device_event_id,
            }
        )
        return

    ev = TripEvent(
        event_id=event_id,
        device_event_id=device_event_id,
        trip_id=trip_id,
        truck_id=truck_id,
        driver_id=driver_id,
        event_type="driver_feedback",
        category=cfg.category,
        priority=Priority(str(cfg.priority.value)),
        timestamp=now,
        offset_seconds=0,
        source=Source.SYSTEM,
    )
    payload = ev.model_dump_json()
    proc_key = RedisSchema.Telemetry.processed(truck_id)
    tier = PRIORITY_MAP.get(str(cfg.priority.value), 6)
    sort_score = processed_queue_sort_score(ev.timestamp, tier)
    await redis.push_to_processed(proc_key, payload, score=sort_score)

    logger.info(
        {
            "action": "feedback_injected",
            "trip_id": trip_id,
            "style": style,
            "rating": rating,
            "truck_id": truck_id,
        }
    )
