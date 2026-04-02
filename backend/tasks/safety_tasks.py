"""
Safety Agent Celery Tasks

Registers tasks for Safety Agent with Celery.
Celery automatically discovers these when workers start.

Queue: safety_queue
Tasks:
  - tasks.safety_tasks.analyse_event: Main safety analysis
"""

import asyncio
import logging

from agents.safety.agent import SafetyAgent
from celery_app import app
from common.db.engine import engine
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


@app.task(bind=True, queue="safety_queue", max_retries=3)
def analyse_event(self, intent_capsule: dict) -> dict:
    """
    Celery task: Analyze safety event.

    Called by Orchestrator with IntentCapsule.
    Deserializes capsule, instantiates SafetyAgent, runs it.

    Args:
        self: Celery task instance (for retries)
        intent_capsule: Dict representation of IntentCapsule

    Returns:
        Agent result dict (will be stored in Redis)
    """
    try:
        redis = RedisClient()
        agent = SafetyAgent(engine=engine, redis_client=redis)
        result = asyncio.run(agent.run(intent_capsule))
        return result

    except Exception as exc:
        logger.error(
            {
                "action": "safety_task_error",
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        # Retry with exponential backoff: 2^retries seconds
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
