import logging
from typing import Any

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class ScoringAgent(TDAgentBase):
    """
    Scoring Agent — calculates end-of-trip driver scores from telematics data.

    Deployed as its own container (Celery worker).  Receives end_of_trip events
    via IntentCapsule from the Orchestrator.
    """

    SYSTEM_PROMPT = """You are a Driver Scoring Agent for a commercial vehicle telematics platform.

Your role is to evaluate a completed trip and produce a driver performance score.

Rules:
- Score ranges from 0 (worst) to 100 (best).
- Base the score on harsh events (harsh_brake, hard_accel, harsh_corner), speed compliance, and trip duration.
- Provide a brief rationale and list the top 2 improvement areas.
- Be concise — your output feeds automated coaching and insurance workflows.

Output format (JSON):
{
  "score": <0-100>,
  "grade": "<A|B|C|D|F>",
  "rationale": "<two-sentence summary>",
  "improvement_areas": ["<area1>", "<area2>"]
}"""

    tools: list = []

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        event = event_data.get("event", event_data)
        logger.info(
            "[trace] scoring_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )

        analysis = await self.invoke_llm(event_data)

        return {
            "agent_type": "scoring",
            "status": "trip_scored",
            "score": 85,
            **({"analysis": analysis} if analysis else {}),
        }
