import logging
from typing import Any

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SupportAgent(TDAgentBase):
    """
    Driver Support Agent — generates personalised coaching tips for drivers.

    Deployed as its own container (Celery worker).  Receives events routed by
    the Orchestrator that require driver-facing guidance.
    """

    SYSTEM_PROMPT = """You are a Driver Support and Coaching Agent for a commercial vehicle telematics platform.

Your role is to generate personalised, actionable coaching messages for drivers based on their telematics events.

Rules:
- Tone: supportive, professional, non-judgmental.
- Keep coaching tips practical and specific to the event.
- Reference the event type and any relevant context (speed, g-force, location).
- Limit the tip to 2-3 sentences.

Output format (JSON):
{
  "coaching_tip": "<personalised tip for the driver>",
  "priority": "<routine|important|urgent>"
}"""

    tools: list = []

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        event = event_data.get("event", event_data)
        logger.info(
            "[trace] support_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )

        analysis = await self.invoke_llm(event_data)

        return {
            "agent_type": "support",
            "status": "coaching_generated",
            "tip": "Drive safely!",
            **({"analysis": analysis} if analysis else {}),
        }
