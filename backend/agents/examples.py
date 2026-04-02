"""Example agents for docs and PoC tests (e.g. weather + traffic tools)."""

from agents.base.agent import Agent
from agents.tools import get_traffic, get_weather
from common.config.system_prompts import PromptType, get_prompt


class WeatherTrafficAgent(Agent):
    """LangGraph ReAct agent with weather and traffic tools."""

    def __init__(self, llm):
        super().__init__(
            llm=llm,
            agent_name="WeatherTrafficAgent",
            tools=[get_weather, get_traffic],
            system_prompt=get_prompt(PromptType.WEATHER_TRAFFIC),
        )
