import logging

from agents.base.agent import TDAgentBase

logger = logging.getLogger(__name__)


class SafetyAgent(TDAgentBase):
    async def process_event(self, event_data):
        event = event_data.get("event", {})
        logger.info(
            "[trace] safety_evaluate event_id=%s trip_id=%s event_type=%s",
            event.get("event_id", "unknown"),
            event.get("trip_id", "unknown"),
            event.get("event_type", "unknown"),
        )
        return {
            "agent_type": "safety",
            "status": "incident_analyzed",
            "risk_score": 0.1,
        }
