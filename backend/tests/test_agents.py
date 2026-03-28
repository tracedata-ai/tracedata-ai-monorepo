"""
Tests for the BaseAgent thick base class and concrete agent implementations.

These tests are intentionally **offline** — they do not call the OpenAI API
(``OPENAI_API_KEY`` is not required).  They validate:

- Graph construction and compilation without errors.
- That subclasses with a missing ``SYSTEM_PROMPT`` raise ``ValueError``.
- The tool-binding and routing wiring of the graph.
- That concrete agents (``OrchestratorAgent``, ``FeedbackAgent``) expose the
  expected tools.
- That ``format_coaching_report`` produces correct structured output.
- That ``_identify_improvement_areas`` returns sensible labels.
"""

from __future__ import annotations

import pytest
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from agents.base import AgentState, BaseAgent
from agents.feedback import (
    FeedbackAgent,
    _identify_improvement_areas,
    format_coaching_report,
)
from agents.orchestrator import OrchestratorAgent

# ---------------------------------------------------------------------------
# Helpers — minimal offline-safe concrete agent
# ---------------------------------------------------------------------------


class _MinimalAgent(BaseAgent):
    """Simplest possible subclass — no tools, valid system prompt."""

    SYSTEM_PROMPT = "You are a test agent."


@tool
def _echo_tool(text: str) -> str:
    """Return the input unchanged."""
    return text


class _ToolAgent(BaseAgent):
    """Agent with one dummy tool to verify tool-binding path."""

    SYSTEM_PROMPT = "You are a tool-using test agent."
    tools = [_echo_tool]


# ---------------------------------------------------------------------------
# BaseAgent construction
# ---------------------------------------------------------------------------


class TestBaseAgentConstruction:
    def test_minimal_agent_compiles_without_error(self) -> None:
        agent = _MinimalAgent()
        assert agent.graph is not None

    def test_empty_system_prompt_raises_value_error(self) -> None:
        class _Bad(BaseAgent):
            SYSTEM_PROMPT = ""

        with pytest.raises(ValueError, match="SYSTEM_PROMPT"):
            _Bad()

    def test_missing_system_prompt_raises_value_error(self) -> None:
        """Concrete class that forgets to set SYSTEM_PROMPT should fail."""

        class _Forgot(BaseAgent):
            pass

        with pytest.raises(ValueError, match="SYSTEM_PROMPT"):
            _Forgot()

    def test_custom_checkpointer_is_accepted(self) -> None:
        checkpointer = MemorySaver()
        agent = _MinimalAgent(checkpointer=checkpointer)
        assert agent._checkpointer is checkpointer

    def test_graph_property_returns_compiled_graph(self) -> None:
        agent = _MinimalAgent()
        # The compiled graph has a ``get_graph()`` method in LangGraph.
        assert hasattr(agent.graph, "get_graph")

    def test_tool_agent_compiles_without_error(self) -> None:
        agent = _ToolAgent()
        assert agent.graph is not None


# ---------------------------------------------------------------------------
# BaseAgent._build_config
# ---------------------------------------------------------------------------


class TestBuildConfig:
    def test_explicit_thread_id_is_preserved(self) -> None:
        agent = _MinimalAgent()
        config = agent._build_config("my-thread", None)
        assert config["configurable"]["thread_id"] == "my-thread"

    def test_no_thread_id_generates_uuid(self) -> None:
        import re

        agent = _MinimalAgent()
        config = agent._build_config(None, None)
        tid = config["configurable"]["thread_id"]
        uuid_pattern = re.compile(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
        )
        assert uuid_pattern.match(tid), f"Expected UUID, got: {tid}"

    def test_extra_config_is_merged(self) -> None:
        agent = _MinimalAgent()
        config = agent._build_config("t1", {"recursion_limit": 5})
        assert config["configurable"]["recursion_limit"] == 5
        assert config["configurable"]["thread_id"] == "t1"


# ---------------------------------------------------------------------------
# BaseAgent._build_initial_state
# ---------------------------------------------------------------------------


class TestBuildInitialState:
    def test_initial_state_contains_user_message(self) -> None:
        agent = _MinimalAgent()
        state = agent._build_initial_state("Hello", "t1")
        assert state["messages"][0]["role"] == "user"
        assert state["messages"][0]["content"] == "Hello"


# ---------------------------------------------------------------------------
# AgentState type
# ---------------------------------------------------------------------------


class TestAgentState:
    def test_agent_state_is_typed_dict(self) -> None:
        # Verify AgentState has the expected 'messages' key annotation.
        assert "messages" in AgentState.__annotations__


# ---------------------------------------------------------------------------
# OrchestratorAgent
# ---------------------------------------------------------------------------


class TestOrchestratorAgent:
    def test_instantiates_without_error(self) -> None:
        agent = OrchestratorAgent()
        assert agent.graph is not None

    def test_has_expected_tools(self) -> None:
        tool_names = {t.name for t in OrchestratorAgent.tools}
        assert "route_to_safety_agent" in tool_names
        assert "route_to_feedback_agent" in tool_names
        assert "route_to_behavior_agent" in tool_names

    def test_system_prompt_is_non_empty(self) -> None:
        assert OrchestratorAgent.SYSTEM_PROMPT.strip()

    def test_default_model(self) -> None:
        assert OrchestratorAgent.model == "gpt-4.1-mini"


# ---------------------------------------------------------------------------
# FeedbackAgent
# ---------------------------------------------------------------------------


class TestFeedbackAgent:
    def test_instantiates_without_error(self) -> None:
        agent = FeedbackAgent()
        assert agent.graph is not None

    def test_has_format_coaching_report_tool(self) -> None:
        tool_names = {t.name for t in FeedbackAgent.tools}
        assert "format_coaching_report" in tool_names

    def test_system_prompt_is_non_empty(self) -> None:
        assert FeedbackAgent.SYSTEM_PROMPT.strip()


# ---------------------------------------------------------------------------
# format_coaching_report tool (pure-function, no LLM call needed)
# ---------------------------------------------------------------------------


class TestFormatCoachingReport:
    def test_low_risk_high_score(self) -> None:
        result = format_coaching_report.invoke(
            {
                "driver_id": "D-001",
                "score": 90.0,
                "harsh_braking": 0,
                "speeding": 0,
                "harsh_cornering": 1,
                "trip_distance_km": 50.0,
            }
        )
        assert result["risk_level"] == "low"
        assert result["overall_score"] == 90.0
        assert result["incidents"]["total"] == 1

    def test_high_risk_low_score(self) -> None:
        result = format_coaching_report.invoke(
            {
                "driver_id": "D-002",
                "score": 45.0,
                "harsh_braking": 5,
                "speeding": 3,
                "harsh_cornering": 4,
                "trip_distance_km": 30.0,
            }
        )
        assert result["risk_level"] == "high"
        assert result["incidents"]["total"] == 12

    def test_incidents_per_100km_calculation(self) -> None:
        result = format_coaching_report.invoke(
            {
                "driver_id": "D-003",
                "score": 70.0,
                "harsh_braking": 2,
                "speeding": 0,
                "harsh_cornering": 0,
                "trip_distance_km": 100.0,
            }
        )
        assert result["incidents_per_100km"] == 2.0

    def test_zero_distance_does_not_raise(self) -> None:
        result = format_coaching_report.invoke(
            {
                "driver_id": "D-004",
                "score": 75.0,
                "harsh_braking": 0,
                "speeding": 0,
                "harsh_cornering": 0,
                "trip_distance_km": 0.0,
            }
        )
        assert result["incidents_per_100km"] == 0.0

    def test_invalid_score_raises(self) -> None:
        with pytest.raises(ValueError, match="score must be between 0 and 100"):
            format_coaching_report.invoke(
                {
                    "driver_id": "D-005",
                    "score": 150.0,
                    "harsh_braking": 0,
                    "speeding": 0,
                    "harsh_cornering": 0,
                    "trip_distance_km": 10.0,
                }
            )

    def test_medium_risk_boundary(self) -> None:
        result = format_coaching_report.invoke(
            {
                "driver_id": "D-006",
                "score": 60.0,
                "harsh_braking": 1,
                "speeding": 1,
                "harsh_cornering": 0,
                "trip_distance_km": 20.0,
            }
        )
        assert result["risk_level"] == "medium"


# ---------------------------------------------------------------------------
# _identify_improvement_areas helper
# ---------------------------------------------------------------------------


class TestIdentifyImprovementAreas:
    def test_all_zeros_returns_general_maintenance(self) -> None:
        areas = _identify_improvement_areas(0, 0, 0)
        assert len(areas) == 1
        assert "good" in areas[0]

    def test_high_harsh_braking_flagged(self) -> None:
        areas = _identify_improvement_areas(5, 0, 0)
        assert "braking smoothness" in areas

    def test_any_speeding_flagged(self) -> None:
        areas = _identify_improvement_areas(0, 1, 0)
        assert "speed compliance" in areas

    def test_high_harsh_cornering_flagged(self) -> None:
        areas = _identify_improvement_areas(0, 0, 4)
        assert "cornering technique" in areas

    def test_multiple_issues_all_flagged(self) -> None:
        areas = _identify_improvement_areas(3, 2, 3)
        assert "braking smoothness" in areas
        assert "speed compliance" in areas
        assert "cornering technique" in areas
