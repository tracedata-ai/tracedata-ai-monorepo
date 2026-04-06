"""
Sentiment Agent — Celery task definition.

Location: backend/agents/sentiment/tasks.py
"""

import logging

from celery import shared_task

from agents.sentiment.agent import SentimentAgent
from common.celery_async import run_async
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


async def _analyse_feedback_async(intent_capsule: dict) -> dict:
    trip_id = intent_capsule.get("trip_id", "unknown")
    redis = RedisClient()
    try:
        agent = SentimentAgent(redis_client=redis)
        result = await agent.run(intent_capsule)
        completion = {
            "trip_id": trip_id,
            "agent": "sentiment",
            "status": "done",
            "final": True,
            "result": result,
        }
        channel = RedisSchema.Trip.events_channel(trip_id)
        await redis.publish_completion(
            channel=channel,
            event=completion,
            ttl=RedisSchema.Trip.EVENT_TTL,
        )
        return completion
    finally:
        await redis.close()


@shared_task(
    bind=True,
    name="tasks.sentiment_tasks.analyse_feedback",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
)
def analyse_feedback(self, intent_capsule: dict) -> dict:
    """
    Sentiment Agent Celery task.

    Sprint 3: RAG + pgvector similarity search.
    """
    trip_id = intent_capsule.get("trip_id", "unknown")

    logger.info(
        {"action": "task_received", "task": "analyse_feedback", "trip_id": trip_id}
    )

    try:
        completion = run_async(_analyse_feedback_async(intent_capsule))
        logger.info(
            {"action": "task_complete", "task": "analyse_feedback", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "analyse_feedback", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
