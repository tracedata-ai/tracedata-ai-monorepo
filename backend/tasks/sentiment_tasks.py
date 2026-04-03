"""
Sentiment Agent Celery Tasks
"""

import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from agents.sentiment.agent import SentimentAgent
from celery_app import app
from common.config.settings import get_settings
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)
settings = get_settings()


@app.task(bind=True, queue=settings.sentiment_queue, max_retries=3)
def analyse_feedback(self, intent_capsule: dict) -> dict:
    """Analyze driver feedback sentiment."""
    try:
        task_engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=settings.debug,
        )
        redis = RedisClient()
        agent = SentimentAgent(engine_param=task_engine, redis_client=redis)
        result = asyncio.run(agent.run(intent_capsule))
        asyncio.run(task_engine.dispose())
        return result

    except Exception as exc:
        logger.error(
            {
                "action": "sentiment_task_error",
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
