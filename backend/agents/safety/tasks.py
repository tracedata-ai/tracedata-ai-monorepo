"""
Safety Agent — Celery task definition.

Location: backend/agents/safety/tasks.py
"""

import asyncio
import logging

from celery import shared_task

from agents.safety.agent import SafetyAgent
from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


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
        agent = SafetyAgent(
            agent_name="SafetyAgent",
            input_queue=settings.safety_queue,
            output_queue=settings.orchestrator_queue,
        )

        # Sprint 2: process_event is a stub that logs and returns
        result = asyncio.run(agent.process_event(intent_capsule))

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
