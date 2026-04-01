"""
Scoring Agent Celery Tasks
"""

import asyncio
import logging

from agents.scoring.agent import ScoringAgent
from celery_app import app
from common.config.settings import get_settings
from common.db.engine import engine
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)
settings = get_settings()
_WORKER_LOOP: asyncio.AbstractEventLoop | None = None


def _run_on_worker_loop(coro):
    """
    Reuse one event loop per Celery worker process.
    Avoids asyncpg pool connections being reused across different loops.
    """
    global _WORKER_LOOP
    if _WORKER_LOOP is None or _WORKER_LOOP.is_closed():
        _WORKER_LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(_WORKER_LOOP)
    return _WORKER_LOOP.run_until_complete(coro)


@app.task(bind=True, queue=settings.scoring_queue, max_retries=3)
def score_trip(self, intent_capsule: dict) -> dict:
    """Score entire trip."""
    try:
        redis = RedisClient()
        agent = ScoringAgent(engine_param=engine, redis_client=redis)
        result = _run_on_worker_loop(agent.run(intent_capsule))
        return result

    except Exception as exc:
        logger.error(
            {
                "action": "scoring_task_error",
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
