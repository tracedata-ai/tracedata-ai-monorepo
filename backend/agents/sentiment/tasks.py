"""
Sentiment Agent — Celery task definition.

Location: backend/agents/sentiment/tasks.py
"""

import asyncio
import logging

from celery import shared_task

from agents.sentiment.agent import SentimentAgent
from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


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

    Sprint 2: stub — returns dummy sentiment result.
    Sprint 3: RAG + pgvector similarity search.
    """
    trip_id = intent_capsule.get("trip_id", "unknown")

    logger.info(
        {"action": "task_received", "task": "analyse_feedback", "trip_id": trip_id}
    )
    logger.info(
        {
            "action": "intent_capsule_received",
            "task": "analyse_feedback",
            "trip_id": trip_id,
            "intent_capsule": intent_capsule,
        }
    )

    try:
        redis = RedisClient()
        agent = SentimentAgent(
            agent_name="SentimentAgent",
            input_queue=settings.sentiment_queue,
            output_queue=settings.orchestrator_queue,
        )

        result = asyncio.run(agent.process_event(intent_capsule))

        completion = {
            "trip_id": trip_id,
            "agent": "sentiment",
            "status": "done",
            "final": True,
            "result": result,
        }
        channel = RedisSchema.Trip.events_channel(trip_id)
        asyncio.run(
            redis.publish_completion(
                channel=channel,
                event=completion,
                ttl=RedisSchema.Trip.EVENT_TTL,
            )
        )

        logger.info(
            {"action": "task_complete", "task": "analyse_feedback", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "analyse_feedback", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
