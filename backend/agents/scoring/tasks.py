"""
Scoring Agent — Celery task definition.

Location: backend/agents/scoring/tasks.py
"""

import asyncio
import logging

from celery import shared_task

from agents.scoring.agent import ScoringAgent
from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

logger = logging.getLogger(__name__)
settings = get_settings()


@shared_task(
    bind=True,
    name="tasks.scoring_tasks.score_trip",
    max_retries=2,
    default_retry_delay=30,
    acks_late=True,
    time_limit=7200,  # 2 hr hard limit (Scoring can take ~1hr)
    soft_time_limit=6900,
)
def score_trip(self, intent_capsule: dict) -> dict:
    """
    Scoring Agent Celery task.

    Sprint 2: stub — returns dummy score.
    Sprint 3: XGBoost inference + SHAP + AIF360.
    """
    trip_id = intent_capsule.get("trip_id", "unknown")

    logger.info({"action": "task_received", "task": "score_trip", "trip_id": trip_id})

    try:
        redis = RedisClient()
        agent = ScoringAgent(
            agent_name="ScoringAgent",
            input_queue=settings.scoring_queue,
            output_queue=settings.orchestrator_queue,
        )

        result = asyncio.run(agent.process_event(intent_capsule))

        completion = {
            "trip_id": trip_id,
            "agent": "scoring",
            "status": "done",
            "priority": 6,  # escalated: LOW → MEDIUM
            "action_sla": "3_days",
            "escalated": True,
            "final": False,
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
            {"action": "task_complete", "task": "score_trip", "trip_id": trip_id}
        )
        return completion

    except Exception as exc:
        logger.exception(
            {"action": "task_failed", "task": "score_trip", "trip_id": trip_id}
        )
        raise self.retry(exc=exc)
