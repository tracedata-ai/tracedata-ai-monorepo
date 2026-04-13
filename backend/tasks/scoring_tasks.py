"""
Scoring Agent Celery Tasks
"""

import logging

from openai import RateLimitError

from agents.scoring.agent import ScoringAgent
from celery_app import app
from common.agent_flow.service import AgentFlowService
from common.celery_async import run_async
from common.config.settings import get_settings
from common.db.engine import engine
from common.models.agent_flow import AgentFlowEvent
from common.redis.client import RedisClient

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
                agent="scoring",
                trip_id=trip_id,
                meta=meta or {},
            )
        )
    finally:
        await redis.close()


@app.task(bind=True, queue=settings.scoring_queue, max_retries=3)
def score_trip(self, intent_capsule: dict) -> dict:
    """Score entire trip."""
    trip_id = intent_capsule.get("trip_id", "unknown")
    run_async(
        _publish_agent_flow(
            trip_id=trip_id,
            status="running",
            meta={"task": "score_trip"},
        )
    )
    try:
        redis = RedisClient()
        agent = ScoringAgent(engine_param=engine, redis_client=redis)
        result = run_async(agent.run(intent_capsule))
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="success",
                meta={"task": "score_trip"},
            )
        )
        return result

    except RateLimitError as exc:
        msg = str(exc).lower()
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "score_trip", "error": "rate_limit"},
            )
        )
        if "requests per day" in msg or "rpd" in msg:
            # Daily quota exhausted — retrying wastes the next quota too
            logger.error({"action": "scoring_rate_limit_daily", "trip_id": trip_id})
            raise  # No retry
        # Per-minute limit — one retry after a fixed pause
        logger.warning({"action": "scoring_rate_limit_rpm", "trip_id": trip_id})
        raise self.retry(exc=exc, countdown=60, max_retries=1) from exc

    except Exception as exc:
        run_async(
            _publish_agent_flow(
                trip_id=trip_id,
                status="error",
                meta={"task": "score_trip", "error": str(exc)[:200]},
            )
        )
        logger.error(
            {
                "action": "scoring_task_error",
                "error": str(exc),
                "retry_count": self.request.retries,
            }
        )
        raise self.retry(exc=exc, countdown=2**self.request.retries) from exc
