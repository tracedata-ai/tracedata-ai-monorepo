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
    results_queue = "td:orchestrator:results"
    # Logic to pick which agent to start based on env var or arg
    agent_type = sys.argv[1] if len(sys.argv) > 1 else "orchestrator"
    logger.info("[worker] booting agent_type=%s", agent_type)

    if agent_type == "safety":
        agent = SafetyAgent("SafetyAgent", settings.safety_queue, results_queue)
    elif agent_type == "scoring":
        agent = ScoringAgent("ScoringAgent", settings.scoring_queue, results_queue)
    elif agent_type == "support":
        agent = SupportAgent("SupportAgent", settings.support_queue, results_queue)
    elif agent_type == "sentiment":
        agent = SentimentAgent(
            "SentimentAgent", settings.sentiment_queue, results_queue
        )
    else:
        # Orchestrator dispatches to multiple agent queues, but for the base class pattern,
        # we'll point it to a dedicated results/dispatch queue.
        agent = OrchestratorAgent(
            "OrchestratorAgent", settings.orchestrator_queue, "td:orchestrator:results"
        )

    logger.info(
        "[worker] starting agent_name=%s input_queue=%s output_queue=%s",
        agent.agent_name,
        agent.input_queue,
        agent.output_queue,
    )

    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
