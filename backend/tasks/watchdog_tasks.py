"""
Watchdog and queue observability Celery tasks.

These tasks are triggered by Celery beat (see `celery_app.py`).
"""

import asyncio
import json
import logging
from datetime import UTC, datetime, timedelta
from inspect import isawaitable

from celery import current_app as celery, shared_task
from sqlalchemy import text

from agents.orchestrator.db_manager import DBManager
from common.agent_flow.service import AgentFlowService
from common.config.events import PRIORITY_MAP, processed_queue_sort_score
from common.config.settings import get_settings
from common.db.engine import engine
from common.integrations.slack_notifier import SlackNotifier
from common.models.agent_flow import AgentFlowEvent
from common.models.enums import Priority
from common.models.events import TripEvent
from common.models.security import IntentCapsule, ScopedToken
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()
slack = SlackNotifier()

HEALTH_STATE_KEY_PREFIX = "ops:health:agent"
QUEUE_DEGRADED_THRESHOLD = 20
QUEUE_DOWN_THRESHOLD = 100


@shared_task(
    bind=True,
    name="tasks.watchdog_tasks.reset_stuck_events",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
)
def reset_stuck_events(self) -> dict:
    """
    Recover events stuck in `processing` beyond lock TTL.

    Safety invariant: recovery targets only `status='processing'`.
    HITL rows (`status='locked'`) are never reset.
    """
    try:
        db = DBManager()
        result = asyncio.run(db.watchdog())
        return {"status": "ok", "task": "reset_stuck_events", "result": result}
    except Exception as exc:
        logger.exception({"action": "watchdog_reset_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


@shared_task(
    bind=True,
    name="tasks.watchdog_tasks.publish_queue_depths",
    max_retries=1,
    default_retry_delay=15,
    acks_late=True,
)
def publish_queue_depths(self) -> dict:
    """Emit periodic queue depth diagnostics for observability."""
    try:
        queue_sizes = asyncio.run(_run_publish_queue_depths())
        logger.info({"action": "queue_depths", "queues": queue_sizes})
        return {"status": "ok", "task": "publish_queue_depths", "queues": queue_sizes}
    except Exception as exc:
        logger.exception({"action": "queue_depths_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


async def _run_publish_queue_depths() -> dict[str, int]:
    """Single event-loop entry point for publish_queue_depths.

    All three async steps share one RedisClient and one event loop so that
    the connection created in _collect_queue_sizes is still alive when
    _publish_worker_health and _alert_worker_health_transitions use it.
    """
    redis = RedisClient()
    try:
        queue_sizes = await _collect_queue_sizes(redis)
        await _publish_worker_health(redis, queue_sizes)
        await _alert_worker_health_transitions(redis, queue_sizes)
        return queue_sizes
    except Exception:
        await slack.send_ops_alert(
            component="watchdog",
            severity="critical",
            message="Queue depth monitor failed",
            details={},
        )
        raise
    finally:
        close_result = redis.close()
        if isawaitable(close_result):
            await close_result


async def _collect_queue_sizes(redis: RedisClient) -> dict[str, int]:
    client = redis._client
    keys = [
        "td:ingestion:events",
        "td:orchestrator:events",
        "td:agent:safety",
        "td:agent:scoring",
        "td:agent:support",
        "td:agent:sentiment",
    ]
    out: dict[str, int] = {}
    for key in keys:
        # Celery queues are lists; pipeline queues are zsets.
        zset_count = await client.zcard(key)
        out[key] = zset_count if zset_count > 0 else await client.llen(key)
    return out


async def _publish_worker_health(
    redis: RedisClient,
    queue_sizes: dict[str, int],
) -> None:
    service = AgentFlowService(redis)
    queue_to_agent = {
        settings.orchestrator_queue: "orchestrator",
        settings.safety_queue: "safety",
        settings.scoring_queue: "scoring",
        settings.sentiment_queue: "sentiment",
        settings.support_queue: "support",
    }
    for queue_name, agent in queue_to_agent.items():
        depth = int(queue_sizes.get(queue_name, 0))
        status = "healthy"
        if depth > QUEUE_DOWN_THRESHOLD:
            status = "unhealthy"
        elif depth > QUEUE_DEGRADED_THRESHOLD:
            status = "degraded"

        await service.publish_event(
            AgentFlowEvent(
                event_type="worker_health",
                status=status,  # type: ignore[arg-type]
                agent=agent,  # type: ignore[arg-type]
                meta={"queue": queue_name, "depth": depth},
            )
        )


async def _alert_worker_health_transitions(
    redis: RedisClient,
    queue_sizes: dict[str, int],
) -> None:
    queue_to_agent = {
        settings.orchestrator_queue: "orchestrator",
        settings.safety_queue: "safety",
        settings.scoring_queue: "scoring",
        settings.sentiment_queue: "sentiment",
        settings.support_queue: "support",
    }
    client = redis._client

    for queue_name, agent in queue_to_agent.items():
        depth = int(queue_sizes.get(queue_name, 0))
        if depth > QUEUE_DOWN_THRESHOLD:
            current_state = "down"
        elif depth > QUEUE_DEGRADED_THRESHOLD:
            current_state = "degraded"
        else:
            current_state = "online"

        state_key = f"{HEALTH_STATE_KEY_PREFIX}:{agent}:state"
        previous_state_raw = client.get(state_key)
        if isawaitable(previous_state_raw):
            previous_state_raw = await previous_state_raw
        previous_state = (
            previous_state_raw.decode("utf-8")
            if isinstance(previous_state_raw, (bytes, bytearray))
            else str(previous_state_raw) if previous_state_raw else None
        )

        if previous_state == current_state:
            continue

        set_result = client.set(state_key, current_state)
        if isawaitable(set_result):
            await set_result

        if previous_state is None and current_state == "online":
            await slack.send_ops_alert(
                component=f"agent:{agent}",
                severity="info",
                message="ONLINE",
                details={"queue": queue_name, "depth": depth},
            )
            continue

        if current_state == "online":
            await slack.send_ops_alert(
                component=f"agent:{agent}",
                severity="info",
                message="RECOVERED",
                details={
                    "from_state": previous_state,
                    "queue": queue_name,
                    "depth": depth,
                },
            )
        elif current_state == "degraded":
            await slack.send_ops_alert(
                component=f"agent:{agent}",
                severity="warning",
                message="DEGRADED",
                details={
                    "from_state": previous_state,
                    "queue": queue_name,
                    "depth": depth,
                },
            )
        else:
            await slack.send_ops_alert(
                component=f"agent:{agent}",
                severity="critical",
                message="DOWN",
                details={
                    "from_state": previous_state,
                    "queue": queue_name,
                    "depth": depth,
                },
            )


# ── Re-scoring watchdog ───────────────────────────────────────────────────────


@shared_task(
    bind=True,
    name="tasks.watchdog_tasks.rescore_unscored_trips",
    max_retries=1,
    default_retry_delay=60,
    acks_late=True,
)
def rescore_unscored_trips(self) -> dict:
    """
    Find completed trips with no score in scoring_schema and re-dispatch
    scoring — but only when the Redis all_pings cache is still alive.

    Runs every 5 minutes via Celery beat. Caps at 10 dispatches per run
    to avoid queue flooding.
    """
    try:
        result = asyncio.run(_find_and_rescore())
        logger.info({"action": "rescore_watchdog_complete", **result})
        return {"status": "ok", "task": "rescore_unscored_trips", **result}
    except Exception as exc:
        logger.exception({"action": "rescore_watchdog_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


async def _find_and_rescore() -> dict:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(hours=2)

    async with engine.connect() as conn:
        rows = (
            (
                await conn.execute(
                    text("""
                    SELECT pt.trip_id, pt.driver_id
                    FROM   pipeline_trips pt
                    WHERE  pt.status   = 'complete'
                      AND  pt.closed_at > :cutoff
                      AND  NOT EXISTS (
                               SELECT 1
                               FROM   scoring_schema.trip_scores ts
                               WHERE  ts.trip_id = pt.trip_id
                           )
                    ORDER  BY pt.closed_at DESC
                    LIMIT  10
                """),
                    {"cutoff": cutoff},
                )
            )
            .mappings()
            .all()
        )

    if not rows:
        return {"dispatched": 0, "skipped": 0, "reason": "none_pending"}

    redis = RedisClient()
    dispatched = 0
    skipped = 0

    try:
        for row in rows:
            trip_id = str(row["trip_id"])
            all_pings_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "all_pings")

            if not await redis._client.exists(all_pings_key):
                skipped += 1
                logger.info({"action": "rescore_skip_no_cache", "trip_id": trip_id})
                continue

            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, "scoring", "all_pings"),
                RedisSchema.Trip.agent_data(trip_id, "scoring", "historical_avg"),
                RedisSchema.Trip.agent_data(trip_id, "scoring", "trip_context"),
            ]
            token = ScopedToken(
                agent="scoring",
                trip_id=trip_id,
                expires_at=datetime.now(UTC),
                read_keys=read_keys,
                write_keys=[RedisSchema.Trip.output(trip_id, "scoring")],
            )
            capsule = IntentCapsule(
                trip_id=trip_id,
                agent="scoring",
                device_event_id="watchdog-rescore",
                priority=5,
                tool_whitelist=["redis_read", "redis_write"],
                step_to_tools={"1": ["redis_read"], "2": ["redis_write"]},
                ttl_seconds=600,
                issued_by="watchdog",
                token=token,
            )
            celery.send_task(
                "tasks.scoring_tasks.score_trip",
                kwargs={"intent_capsule": capsule.model_dump()},
                queue=settings.scoring_queue,
                priority=5,
            )
            dispatched += 1
            logger.info({"action": "rescore_dispatched", "trip_id": trip_id})
    finally:
        close = redis.close()
        if isawaitable(close):
            await close

    return {"dispatched": dispatched, "skipped": skipped}


# ── Re-queue stuck received events ────────────────────────────────────────────


@shared_task(
    bind=True,
    name="tasks.watchdog_tasks.requeue_stuck_received_events",
    max_retries=1,
    default_retry_delay=30,
    acks_late=True,
)
def requeue_stuck_received_events(self) -> dict:
    """
    Find pipeline_events stuck in 'received' (never picked up by orchestrator)
    and re-push TripEvent JSON to the orchestrator ZSet queue.

    Handles Redis message loss (e.g., Redis restart between ingestion and
    orchestrator consumption). Skips rows with retry_count >= 3.
    Capped at 20 per run to avoid queue flooding.
    """
    try:
        result = asyncio.run(_find_and_requeue_received())
        logger.info({"action": "requeue_received_complete", **result})
        return {"status": "ok", "task": "requeue_stuck_received_events", **result}
    except Exception as exc:
        logger.exception({"action": "requeue_received_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


async def _find_and_requeue_received() -> dict:
    cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=10)

    async with engine.connect() as conn:
        rows = (
            (
                await conn.execute(
                    text("""
                    SELECT
                        event_id, device_event_id, trip_id, driver_id, truck_id,
                        event_type, category, priority, timestamp, offset_seconds,
                        details
                    FROM   pipeline_events
                    WHERE  status     = 'received'
                    AND    locked_by  IS NULL
                    AND    ingested_at < :cutoff
                    AND    retry_count < 3
                    ORDER  BY ingested_at ASC
                    LIMIT  20
                """),
                    {"cutoff": cutoff},
                )
            )
            .mappings()
            .all()
        )

    if not rows:
        return {"requeued": 0, "reason": "none_pending"}

    redis = RedisClient()
    requeued = 0

    try:
        for row in rows:
            try:
                priority_str = (row["priority"] or "medium").lower()
                try:
                    priority = Priority(priority_str)
                except ValueError:
                    priority = Priority.MEDIUM
                priority_tier = PRIORITY_MAP.get(priority_str, 6)

                ts = row["timestamp"]
                if ts is None:
                    continue
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=UTC)

                details = row["details"]
                if not isinstance(details, dict):
                    details = {}

                event = TripEvent(
                    event_id=str(row["event_id"]),
                    device_event_id=str(row["device_event_id"]),
                    trip_id=str(row["trip_id"]),
                    truck_id=str(row["truck_id"]),
                    driver_id=str(row["driver_id"]),
                    event_type=str(row["event_type"]),
                    category=str(row["category"] or "unknown"),
                    priority=priority,
                    timestamp=ts,
                    offset_seconds=int(row["offset_seconds"] or 0),
                    details=details,
                )
                score = processed_queue_sort_score(ts, priority_tier)
                await redis._client.zadd(
                    settings.orchestrator_queue,
                    {event.model_dump_json(): score},
                )
                requeued += 1
                logger.info(
                    {
                        "action": "received_event_requeued",
                        "device_event_id": str(row["device_event_id"]),
                        "trip_id": str(row["trip_id"]),
                    }
                )
            except Exception as row_exc:
                logger.warning(
                    {
                        "action": "requeue_received_row_error",
                        "device_event_id": str(row.get("device_event_id", "?")),
                        "error": str(row_exc)[:120],
                    }
                )
    finally:
        close = redis.close()
        if isawaitable(close):
            await close

    return {"requeued": requeued}


# ── Re-queue stuck scoring / coaching trips ───────────────────────────────────


@shared_task(
    bind=True,
    name="tasks.watchdog_tasks.requeue_stuck_trips",
    max_retries=1,
    default_retry_delay=60,
    acks_late=True,
)
def requeue_stuck_trips(self) -> dict:
    """
    Find trips stuck in scoring_pending or coaching_pending beyond thresholds
    and re-dispatch to the appropriate agent queue if the Redis cache is alive.

    Thresholds:
      scoring_pending  → 15 minutes  (scoring agent crashed / capsule expired)
      coaching_pending → 30 minutes  (support agent crashed)

    Runs every 10 minutes via Celery beat. Capped at 10 dispatches per status.
    """
    try:
        result = asyncio.run(_find_and_requeue_stuck_trips())
        logger.info({"action": "requeue_stuck_trips_complete", **result})
        return {"status": "ok", "task": "requeue_stuck_trips", **result}
    except Exception as exc:
        logger.exception({"action": "requeue_stuck_trips_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


async def _rewarm_support_cache(redis: RedisClient, trip_id: str) -> bool:
    """
    Rebuild trips:{trip_id}:support:trip_context from DB when the original
    warm cache has expired.  Returns True if the key was successfully written.
    """
    async with engine.connect() as conn:
        score_row = (
            (
                await conn.execute(
                    text("""
                    SELECT score, score_breakdown, scoring_narrative
                    FROM   scoring_schema.trip_scores
                    WHERE  trip_id::text = :tid
                    ORDER  BY created_at DESC
                    LIMIT  1
                """),
                    {"tid": trip_id},
                )
            )
            .mappings()
            .first()
        )

        trip_row = (
            (
                await conn.execute(
                    text("""
                    SELECT driver_id, truck_id, started_at, ended_at
                    FROM   pipeline_trips
                    WHERE  trip_id::text = :tid
                """),
                    {"tid": trip_id},
                )
            )
            .mappings()
            .first()
        )

    if not trip_row:
        return False

    scoring_output: dict | None = None
    if score_row:
        breakdown = score_row["score_breakdown"]
        if isinstance(breakdown, str):
            try:
                breakdown = json.loads(breakdown)
            except Exception:
                breakdown = {}
        scoring_output = {
            "score": float(score_row["score"]),
            "trip_score": float(score_row["score"]),
            "score_breakdown": breakdown or {},
            "scoring_narrative": score_row["scoring_narrative"],
        }

    trip_context = {
        "trip_id": trip_id,
        "driver_id": str(trip_row["driver_id"]),
        "truck_id": str(trip_row["truck_id"]),
        "started_at": (
            trip_row["started_at"].isoformat() if trip_row["started_at"] else None
        ),
        "ended_at": trip_row["ended_at"].isoformat() if trip_row["ended_at"] else None,
        "scoring_output": scoring_output,
        "safety_output": None,
        "_rewarmed_by": "watchdog",
    }

    trip_context_key = RedisSchema.Trip.agent_data(trip_id, "support", "trip_context")
    coaching_history_key = RedisSchema.Trip.agent_data(
        trip_id, "support", "coaching_history"
    )
    # 300s TTL — enough for the agent to consume, short enough not to pollute cache
    await redis._client.set(trip_context_key, json.dumps(trip_context), ex=300)
    await redis._client.set(coaching_history_key, json.dumps([]), ex=300)
    return True


async def _find_and_requeue_stuck_trips() -> dict:
    scoring_cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=15)
    coaching_cutoff = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=30)

    async with engine.connect() as conn:
        scoring_rows = (
            (
                await conn.execute(
                    text("""
                    SELECT trip_id, driver_id
                    FROM   pipeline_trips
                    WHERE  status = 'scoring_pending'
                    AND    updated_at < :cutoff
                    ORDER  BY updated_at ASC
                    LIMIT  10
                """),
                    {"cutoff": scoring_cutoff},
                )
            )
            .mappings()
            .all()
        )

        coaching_rows = (
            (
                await conn.execute(
                    text("""
                    SELECT trip_id, driver_id
                    FROM   pipeline_trips
                    WHERE  status = 'coaching_pending'
                    AND    updated_at < :cutoff
                    ORDER  BY updated_at ASC
                    LIMIT  10
                """),
                    {"cutoff": coaching_cutoff},
                )
            )
            .mappings()
            .all()
        )

    redis = RedisClient()
    scoring_dispatched = 0
    scoring_skipped = 0
    coaching_dispatched = 0
    coaching_skipped = 0

    try:
        # ── Re-dispatch scoring ────────────────────────────────────────────────
        for row in scoring_rows:
            trip_id = str(row["trip_id"])
            all_pings_key = RedisSchema.Trip.agent_data(trip_id, "scoring", "all_pings")
            if not await redis._client.exists(all_pings_key):
                scoring_skipped += 1
                logger.info(
                    {"action": "requeue_scoring_skip_no_cache", "trip_id": trip_id}
                )
                continue

            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, "scoring", "all_pings"),
                RedisSchema.Trip.agent_data(trip_id, "scoring", "historical_avg"),
                RedisSchema.Trip.agent_data(trip_id, "scoring", "trip_context"),
            ]
            token = ScopedToken(
                agent="scoring",
                trip_id=trip_id,
                expires_at=datetime.now(UTC),
                read_keys=read_keys,
                write_keys=[RedisSchema.Trip.output(trip_id, "scoring")],
            )
            capsule = IntentCapsule(
                trip_id=trip_id,
                agent="scoring",
                device_event_id="watchdog-requeue-scoring",
                priority=5,
                tool_whitelist=["redis_read", "redis_write"],
                step_to_tools={"1": ["redis_read"], "2": ["redis_write"]},
                ttl_seconds=600,
                issued_by="watchdog",
                token=token,
            )
            celery.send_task(
                "tasks.scoring_tasks.score_trip",
                kwargs={"intent_capsule": capsule.model_dump()},
                queue=settings.scoring_queue,
                priority=5,
            )
            scoring_dispatched += 1
            logger.info({"action": "requeue_scoring_dispatched", "trip_id": trip_id})

        # ── Re-dispatch coaching / support ─────────────────────────────────────
        for row in coaching_rows:
            trip_id = str(row["trip_id"])
            trip_context_key = RedisSchema.Trip.agent_data(
                trip_id, "support", "trip_context"
            )
            if not await redis._client.exists(trip_context_key):
                # Cache expired — try re-warming from DB before giving up
                warmed = await _rewarm_support_cache(redis, trip_id)
                if not warmed:
                    coaching_skipped += 1
                    logger.info(
                        {"action": "requeue_coaching_skip_no_data", "trip_id": trip_id}
                    )
                    continue
                logger.info(
                    {"action": "requeue_coaching_cache_rewarmed", "trip_id": trip_id}
                )

            read_keys = [
                RedisSchema.Trip.agent_data(trip_id, "support", "trip_context"),
                RedisSchema.Trip.agent_data(trip_id, "support", "coaching_history"),
            ]
            token = ScopedToken(
                agent="support",
                trip_id=trip_id,
                expires_at=datetime.now(UTC),
                read_keys=read_keys,
                write_keys=[
                    RedisSchema.Trip.output(trip_id, "support"),
                    RedisSchema.Trip.events_channel(trip_id),
                ],
            )
            capsule = IntentCapsule(
                trip_id=trip_id,
                agent="support",
                device_event_id="watchdog-requeue-coaching",
                priority=5,
                tool_whitelist=["redis_read", "redis_write"],
                step_to_tools={"1": ["redis_read"], "2": ["redis_write"]},
                ttl_seconds=600,
                issued_by="watchdog",
                token=token,
            )
            celery.send_task(
                "tasks.support_tasks.generate_coaching",
                kwargs={"intent_capsule": capsule.model_dump()},
                queue=settings.support_queue,
                priority=5,
            )
            coaching_dispatched += 1
            logger.info({"action": "requeue_coaching_dispatched", "trip_id": trip_id})

    finally:
        close = redis.close()
        if isawaitable(close):
            await close

    return {
        "scoring_dispatched": scoring_dispatched,
        "scoring_skipped": scoring_skipped,
        "coaching_dispatched": coaching_dispatched,
        "coaching_skipped": coaching_skipped,
    }
