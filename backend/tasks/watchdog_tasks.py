"""
Watchdog and queue observability Celery tasks.

These tasks are triggered by Celery beat (see `celery_app.py`).
"""

import asyncio
import logging

from celery import shared_task

from agents.orchestrator.db_manager import DBManager
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


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
        redis = RedisClient()
        queue_sizes = asyncio.run(_collect_queue_sizes(redis))
        logger.info({"action": "queue_depths", "queues": queue_sizes})
        return {"status": "ok", "task": "publish_queue_depths", "queues": queue_sizes}
    except Exception as exc:
        logger.exception({"action": "queue_depths_failed", "error": str(exc)})
        raise self.retry(exc=exc) from exc


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
