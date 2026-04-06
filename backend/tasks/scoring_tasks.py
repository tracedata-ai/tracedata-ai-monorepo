"""
Scoring Agent Celery Tasks
"""

import logging

from agents.scoring.agent import ScoringAgent
from celery_app import app
from common.celery_async import run_async
from common.config.settings import get_settings
from common.db.engine import engine
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)
settings = get_settings()


@app.task(bind=True, queue=settings.scoring_queue, max_retries=3)
def score_trip(self, intent_capsule: dict) -> dict:
    """Score entire trip."""
    try:
        redis = RedisClient()
        agent = ScoringAgent(engine_param=engine, redis_client=redis)
        result = run_async(agent.run(intent_capsule))
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
