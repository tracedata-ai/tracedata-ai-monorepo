"""
Sentiment Agent Celery Tasks
"""

import asyncio
import logging

from agents.sentiment.agent import SentimentAgent
from celery_app import app
from common.db.engine import engine
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="sentiment_queue", max_retries=3)
def analyse_feedback(self, intent_capsule: dict) -> dict:
    """Analyze driver feedback sentiment."""
    try:
        redis = RedisClient()
        agent = SentimentAgent(engine_param=engine, redis_client=redis)
        result = asyncio.run(agent.run(intent_capsule))
        return result

    except Exception as exc:
        logger.error(
            {
                "action": "sentiment_task_error",
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        raise self.retry(exc=exc, countdown=2**self.request.retries)
