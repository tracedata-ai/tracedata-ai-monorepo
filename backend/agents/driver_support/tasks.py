"""
Driver Support Agent — Celery task definition.

Location: backend/agents/driver_support/tasks.py
"""

import logging

from celery import shared_task
from openai import RateLimitError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from agents.driver_support.agent import SupportAgent
from common.agent_flow.service import AgentFlowService
from common.celery_async import run_async
from common.config.settings import get_settings
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


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
                agent="support",
                trip_id=trip_id,
                meta=meta or {},
            )
        )
    finally:
        await redis.close()


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
    run_async(
        _publish_agent_flow(
            trip_id=trip_id,
            status="running",
            meta={"task": "generate_coaching"},
        )
    )

    try:
        completion = run_async(_generate_coaching_async(intent_capsule))
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="success",
                meta={"task": "generate_coaching"},
            )
        )
        logger.info(
            {"action": "task_complete", "task": "generate_coaching", "trip_id": trip_id}
        )
        return completion

    except RateLimitError as exc:
        msg = str(exc).lower()
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "generate_coaching", "error": "rate_limit"},
            )
        )
        if "requests per day" in msg or "rpd" in msg:
            logger.error({"action": "support_rate_limit_daily", "trip_id": trip_id})
            raise
        logger.warning({"action": "support_rate_limit_rpm", "trip_id": trip_id})
        raise self.retry(exc=exc, countdown=60, max_retries=1) from exc

    except Exception as exc:
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "generate_coaching", "error": str(exc)[:200]},
            )
        )
        logger.exception(
            {"action": "task_failed", "task": "generate_coaching", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
