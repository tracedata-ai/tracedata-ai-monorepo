import logging
from typing import Any

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SafetyAgent(TDAgentBase):
    """
    Safety Agent — analyses driving incidents for risk and generates
    structured safety assessments.

    Deployed as its own container (Celery worker) and receives events via
    IntentCapsule dispatched by the Orchestrator.
    """

    SYSTEM_PROMPT = """You are a Safety Analysis Agent for a commercial vehicle telematics platform.

Your role is to assess driving incident data and produce structured safety evaluations.

Rules:
- Analyse each event objectively based on telemetry data (g-force, speed, location, etc.).
- Rate risk severity as one of: low | medium | high | critical.
- Recommend immediate actions where relevant (e.g., flag for coaching, escalate to fleet manager).
- Be concise — your analysis feeds automated downstream workflows.

Output format (JSON):
{
  "risk_level": "<low|medium|high|critical>",
  "summary": "<one-sentence description>",
  "recommended_action": "<action or null>"
}"""

    tools: list = []

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        event = event_data.get("event", event_data)
        logger.info(
            "[trace] safety_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )

        analysis = await self.invoke_llm(event_data)

        return {
            "agent_type": "safety",
            "status": "incident_analyzed",
            "risk_score": 0.1,
            **({"analysis": analysis} if analysis else {}),
        }
