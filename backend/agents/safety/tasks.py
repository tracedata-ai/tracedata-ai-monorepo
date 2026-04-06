"""
Safety Agent — Celery task definition.

Location: backend/agents/safety/tasks.py
"""

import logging

from celery import shared_task

from agents.safety.agent import SafetyAgent
from common.agent_flow.service import AgentFlowService
from common.celery_async import run_async
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


async def _analyse_event_async(intent_capsule: dict) -> dict:
    trip_id = intent_capsule.get("trip_id", "unknown")
    redis = RedisClient()
    try:
        agent = SafetyAgent(redis_client=redis)
        result = await agent.run(intent_capsule)
        completion = {
            "trip_id": trip_id,
            "agent": "safety",
            "status": "done",
            "final": False,
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


async def _publish_agent_flow(
    *,
    trip_id: str,
    status: str,
    meta: dict | None = None,
) -> None:
    redis = RedisClient()
    try:
        await AgentFlowService(redis).publish_event(
            AgentFlowEvent(
                event_type="agent_running" if status == "running" else "agent_done",
                status=status,  # type: ignore[arg-type]
                agent="safety",
                trip_id=trip_id,
                meta=meta or {},
            )
        )
    finally:
        await redis.close()


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
    run_async(
        _publish_agent_flow(
            trip_id=trip_id,
            status="running",
            meta={"task": "analyse_event"},
        )
    )

    try:
        completion = run_async(_analyse_event_async(intent_capsule))
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="success",
                meta={"task": "analyse_event"},
            )
        )
        logger.info(
            {"action": "task_complete", "task": "analyse_event", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "analyse_event", "error": str(exc)[:200]},
            )
        )
        logger.exception(
            {"action": "task_failed", "task": "analyse_event", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
