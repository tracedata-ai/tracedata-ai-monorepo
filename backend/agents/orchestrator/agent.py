import json
import logging

from agents.base.agent import TDAgentBase
from common.config.settings import get_settings

logger = logging.getLogger(__name__)


class OrchestratorAgent(TDAgentBase):
    async def process_event(self, event_data):
        event = event_data.get("event", {})
        event_type = event.get("event_type")
        event_id = event.get("event_id", "unknown")
        trip_id = event.get("trip_id", "unknown")
        logger.info(
            "[trace] orchestrator_receive event_id=%s trip_id=%s event_type=%s in_queue=%s",
            event_id,
            trip_id,
            event_type,
            self.input_queue,
        )

        if event_type == "harsh_brake":
            settings = get_settings()
            logger.info(
                "[trace] orchestrator_dispatch event_id=%s trip_id=%s event_type=%s out_queue=%s",
                event_id,
                trip_id,
                event_type,
                settings.safety_queue,
            )
            await self.redis.push(settings.safety_queue, json.dumps(event_data))

        return {
            "agent_type": "orchestrator",
            "status": "processed",
            "next_hop": "safety" if event_type == "harsh_brake" else "none",
        }
