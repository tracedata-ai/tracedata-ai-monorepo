import asyncio
import logging
import sys

from agents.driver_support.agent import SupportAgent
from agents.orchestrator.agent import OrchestratorAgent
from agents.safety.agent import SafetyAgent
from agents.scoring.agent import ScoringAgent
from agents.sentiment.agent import SentimentAgent
from common.config.settings import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    settings = get_settings()

    # Logic to pick which agent to start based on env var or arg
    agent_type = sys.argv[1] if len(sys.argv) > 1 else "orchestrator"
    logger.info("[worker] booting agent_type=%s", agent_type)

    if agent_type == "safety":
        agent = SafetyAgent(
            "SafetyAgent", settings.safety_queue, settings.orchestrator_queue
        )
    elif agent_type == "scoring":
        agent = ScoringAgent(
            "ScoringAgent", settings.scoring_queue, settings.orchestrator_queue
        )
    elif agent_type == "support":
        agent = SupportAgent(
            "SupportAgent", settings.support_queue, settings.orchestrator_queue
        )
    elif agent_type == "sentiment":
        agent = SentimentAgent(
            "SentimentAgent", settings.sentiment_queue, settings.orchestrator_queue
        )
    else:
        # Orchestrator dynamically discovers trucks from processed queues
        agent = OrchestratorAgent()
        logger.info("[worker] orchestrator starting (dynamic truck discovery mode)")

    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
