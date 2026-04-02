"""
Safety Agent — Celery task definition.

Location: backend/agents/safety/tasks.py
"""

import asyncio
import logging

from celery import shared_task

from agents.safety.agent import SafetyAgent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="tasks.safety_tasks.analyse_event",
    max_retries=3,
    default_retry_delay=5,
    acks_late=True,
)
def analyse_event(self, intent_capsule: dict) -> dict:
    """
    Safety Agent Celery task.

    Receives IntentCapsule payload from Orchestrator.
    Runs SafetyAgent.process_event() and publishes CompletionEvent.

    Retries: 3 attempts, 5s delay
    Never retries: SecurityViolation (handled in agent)
    """
    trip_id = intent_capsule.get("trip_id", "unknown")
    event_type = intent_capsule.get("event_type", "unknown")

    logger.info(
        {
            "action": "task_received",
            "task": "analyse_event",
            "trip_id": trip_id,
            "event_type": event_type,
        }
    )

    try:
        redis = RedisClient()
        agent = SafetyAgent()

        result = asyncio.run(agent.run(intent_capsule))

        # Publish CompletionEvent
        completion = {
            "trip_id": trip_id,
            "agent": "safety",
            "status": "done",
            "final": False,  # Safety is never the final step
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
            {"action": "task_complete", "task": "analyse_event", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "analyse_event", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
