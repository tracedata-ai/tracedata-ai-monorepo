"""
Sentiment Agent — Celery task definition.

Location: backend/agents/sentiment/tasks.py
"""

import logging

from celery import shared_task
from openai import RateLimitError

from agents.sentiment.agent import SentimentAgent
from common.agent_flow.service import AgentFlowService
from common.celery_async import run_async
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)


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
                agent="sentiment",
                trip_id=trip_id,
                meta=meta or {},
            )
        )
    finally:
        await redis.close()


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
    run_async(
        _publish_agent_flow(
            trip_id=trip_id,
            status="running",
            meta={"task": "analyse_feedback"},
        )
    )

    try:
        completion = run_async(_analyse_feedback_async(intent_capsule))
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="success",
                meta={"task": "analyse_feedback"},
            )
        )
        logger.info(
            {"action": "task_complete", "task": "analyse_feedback", "trip_id": trip_id}
        )
        return completion

    except RateLimitError as exc:
        msg = str(exc).lower()
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "analyse_feedback", "error": "rate_limit"},
            )
        )
        if "requests per day" in msg or "rpd" in msg:
            logger.error({"action": "sentiment_rate_limit_daily", "trip_id": trip_id})
            raise
        logger.warning({"action": "sentiment_rate_limit_rpm", "trip_id": trip_id})
        raise self.retry(exc=exc, countdown=60, max_retries=1) from exc

    except Exception as exc:
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "analyse_feedback", "error": str(exc)[:200]},
            )
        )
        logger.exception(
            {"action": "task_failed", "task": "analyse_feedback", "trip_id": trip_id}
        )
        raise self.retry(exc=exc) from exc
