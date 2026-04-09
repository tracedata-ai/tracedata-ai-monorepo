"""
Watchdog and queue observability Celery tasks.

These tasks are triggered by Celery beat (see `celery_app.py`).
"""

import asyncio
import logging
from inspect import isawaitable

from celery import shared_task

from agents.orchestrator.db_manager import DBManager
from common.agent_flow.service import AgentFlowService
from common.config.settings import get_settings
from common.integrations.slack_notifier import SlackNotifier
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient

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
    redis = RedisClient()
    try:
        queue_sizes = asyncio.run(_collect_queue_sizes(redis))
        asyncio.run(_publish_worker_health(redis, queue_sizes))
        asyncio.run(_alert_worker_health_transitions(redis, queue_sizes))
        logger.info({"action": "queue_depths", "queues": queue_sizes})
        return {"status": "ok", "task": "publish_queue_depths", "queues": queue_sizes}
    except Exception as exc:
        logger.exception({"action": "queue_depths_failed", "error": str(exc)})
        asyncio.run(
            slack.send_ops_alert(
                component="watchdog",
                severity="critical",
                message="Queue depth monitor failed",
                details={"error": str(exc)[:160]},
            )
        )
        raise self.retry(exc=exc) from exc
    finally:
        close_result = redis.close()
        if isawaitable(close_result):
            asyncio.run(close_result)


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
