"""
Driver Support Agent — Celery task definition.

Location: backend/agents/driver_support/tasks.py
"""

import logging

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from agents.driver_support.agent import SupportAgent
from common.celery_async import run_async
from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


async def _generate_coaching_async(intent_capsule: dict) -> dict:
    trip_id = intent_capsule.get("trip_id", "unknown")
    task_engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.debug,
    )
    redis = RedisClient()
    try:
        agent = SupportAgent(engine_param=task_engine, redis_client=redis)
        result = await agent.run(intent_capsule)
        completion = {
            "trip_id": trip_id,
            "agent": "driver_support",
            "status": "done",
            "action_sla": "3_days",
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
        await task_engine.dispose()


@shared_task(
    bind=True,
    name="tasks.support_tasks.generate_coaching",
    max_retries=2,
    default_retry_delay=60,
    acks_late=True,
)
def generate_coaching(self, intent_capsule: dict) -> dict:
    """
    Driver Support Agent Celery task.
    Coaching is batched to end-of-trip — never dispatched mid-trip.
    """
    trip_id = intent_capsule.get("trip_id", "unknown")

    logger.info(
        {"action": "task_received", "task": "generate_coaching", "trip_id": trip_id}
    )

    try:
        completion = run_async(_generate_coaching_async(intent_capsule))
        logger.info(
            {"action": "task_complete", "task": "generate_coaching", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "generate_coaching", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
