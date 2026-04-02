"""
Driver Support Agent — Celery task definition.

Location: backend/agents/driver_support/tasks.py
"""

import asyncio
import logging

from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from agents.driver_support.agent import SupportAgent
from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


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
    Coaching is always batched to end-of-trip — never dispatched mid-trip.

    Sprint 2: stub — returns dummy coaching tips.
    Sprint 3: LLM call with SHAP features + flagged_events.
    """
    trip_id = intent_capsule.get("trip_id", "unknown")

    logger.info(
        {"action": "task_received", "task": "generate_coaching", "trip_id": trip_id}
    )

    try:
        task_engine = create_async_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=settings.debug,
        )
        redis = RedisClient()
        agent = SupportAgent(engine_param=task_engine, redis_client=redis)

        result = asyncio.run(agent.run(intent_capsule))
        asyncio.run(task_engine.dispose())

        completion = {
            "trip_id": trip_id,
            "agent": "driver_support",
            "status": "done",
            "action_sla": "3_days",
            "final": True,  # DSP is last in end-of-trip chain
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
            {"action": "task_complete", "task": "generate_coaching", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "generate_coaching", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
