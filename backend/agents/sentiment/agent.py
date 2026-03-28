import logging
from typing import Any

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SentimentAgent(TDAgentBase):
    """
    Sentiment Agent — classifies driver feedback and disputes.

    Deployed as its own container (Celery worker).  Receives driver_dispute,
    driver_complaint, driver_feedback, and driver_comment events.
    """

    SYSTEM_PROMPT = """You are a Sentiment Analysis Agent for a commercial vehicle telematics platform.

Your role is to classify driver-submitted feedback and flag cases that need human review.

Rules:
- Classify sentiment as: positive | neutral | negative | urgent.
- For negative or urgent items, identify the primary concern category:
  pay_dispute | route_issue | vehicle_condition | fatigue | other.
- Flag for human review (escalate=true) when sentiment is urgent or the concern is pay_dispute.
- Be concise — your output drives automated case routing.

Output format (JSON):
{
  "sentiment": "<positive|neutral|negative|urgent>",
  "concern_category": "<category or null>",
  "escalate": <true|false>,
  "summary": "<one-sentence description>"
}"""

    tools: list = []

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        event = event_data.get("event", event_data)
        logger.info(
            "[trace] sentiment_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )

        analysis = await self.invoke_llm(event_data)

        return {
            "agent_type": "sentiment",
            "status": "feedback_analyzed",
            "sentiment": "positive",
            **({"analysis": analysis} if analysis else {}),
        }
