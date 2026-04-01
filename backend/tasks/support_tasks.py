"""
Support Agent Celery Tasks
"""

import asyncio
import logging

from celery_app import app
from agents.driver_support.agent import SupportAgent
from common.db.engine import engine
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="support_queue", max_retries=3)
def generate_coaching(self, intent_capsule: dict) -> dict:
    """Generate coaching message for driver."""
    try:
        redis = RedisClient()
        agent = SupportAgent(engine_param=engine, redis_client=redis)
        result = asyncio.run(agent.run(intent_capsule))
        return result

    except Exception as exc:
        logger.error({
            "action": "support_task_error",
            "error": str(exc),
            "retry_count": self.request.retries,
        })
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
