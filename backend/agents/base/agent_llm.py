"""Base Agent class with LangGraph integration."""

from abc import ABC
from typing import Any

from langgraph.prebuilt import create_react_agent

from backend.agents.base.logger import get_agent_logger


class Agent(ABC):
    """Base class for all TraceData agents using LangGraph.

    Implements lazy initialization of LangGraph agent and orchestrates
    tool calling with LLM reasoning.
    """

    def __init__(
        self,
        llm: Any,
        agent_name: str,
        tools: list,
        system_prompt: str,
    ):
        """Initialize agent with LLM, tools, and system prompt.

        Args:
            llm: LangChain chat model instance
            agent_name: Name of the agent (used for logging)
            tools: List of LangChain @tool decorated functions
            system_prompt: System prompt that defines agent behavior
        """
        self.llm = llm
        self.agent_name = agent_name
        self.tools = tools
        self.system_prompt = system_prompt
        self._agent = None
        self.logger = get_agent_logger(agent_name)
        self.logger.info(
            "initialized agent | tools=%s | llm=%s",
            [t.name for t in self.tools],
            type(self.llm).__name__,
        )

    def _create_agent(self):
        """Create LangGraph ReactAgent lazily."""
        self.logger.info("creating langgraph agent")
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.system_prompt,
        )

    def invoke(self, input_data: dict) -> dict:
        """Invoke agent with input data.

        Executes the agent's reasoning loop with optional tool calls.

        Args:
            input_data: Input dict, typically {"messages": [{"role": "user", "content": "..."}]}

        Returns:
            Result dict from LangGraph agent invocation
        """
        self.logger.info(
            "invoke start | keys=%s",
            list(input_data.keys()),
        )
        if self._agent is None:
            self._agent = self._create_agent()
        result = self._agent.invoke(input_data)
        self.logger.info("invoke complete")
        return result

    def __repr__(self) -> str:
        return f"{self.agent_name}(tools={len(self.tools)})"

    def __str__(self) -> str:
        tools_str = ", ".join([t.name for t in self.tools])
        return f"{self.agent_name}\n  Tools: {tools_str}\n  LLM: {self.llm}"
