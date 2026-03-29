import logging

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SupportAgent(TDAgentBase):
    async def process_event(self, event_data):
        event = event_data.get("event", {})
        logger.info(
            "[trace] support_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )
        return {
            "agent_type": "support",
            "status": "coaching_generated",
            "tip": "Drive safely!",
        }
