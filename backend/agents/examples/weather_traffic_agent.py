"""Example concrete agents for PoC validation."""

from backend.agents.base.agent_llm import Agent
from backend.agents.tools.weather_traffic import get_traffic, get_weather
from backend.common.config.system_prompts import (
    ORCHESTRATOR_SYSTEM_PROMPT,
    SCORING_SYSTEM_PROMPT,
    WEATHER_TRAFFIC_SYSTEM_PROMPT,
)


class WeatherTrafficAgent(Agent):
    """Example concrete agent: Weather and traffic evaluation.

    This is a minimal PoC agent that demonstrates:
    - Inheriting from Agent ABC
    - Using @tool decorated functions
    - Invoking LLM with tools
    """

    def __init__(self, llm):
        """Initialize weather/traffic agent.

        Args:
            llm: LangChain chat model instance
        """
        super().__init__(
            llm=llm,
            agent_name="WeatherTrafficAgent",
            tools=[get_weather, get_traffic],
            system_prompt=WEATHER_TRAFFIC_SYSTEM_PROMPT,
        )


class ScoringAgentExample(Agent):
    """Example concrete agent: Trip scoring (framework only).

    Full implementation in backend.agents.scoring.agent_v2
    """

    def __init__(self, llm):
        """Initialize scoring agent.

        Args:
            llm: LangChain chat model instance
        """
        super().__init__(
            llm=llm,
            agent_name="ScoringAgent",
            tools=[],  # Tools added in Phase 2
            system_prompt=SCORING_SYSTEM_PROMPT,
        )


class OrchestratorAgentExample(Agent):
    """Example concrete agent: Orchestrator (framework only).

    Full implementation in backend.agents.orchestrator.agent_v2
    """

    def __init__(self, llm):
        """Initialize orchestrator agent.

        Args:
            llm: LangChain chat model instance
        """
        super().__init__(
            llm=llm,
            agent_name="OrchestratorAgent",
            tools=[],  # Tools added in Phase 2
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        )
