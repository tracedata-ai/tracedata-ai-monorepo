"""
Tests for TDAgentBase LangGraph integration.

Strategy:
- No real LLM calls — the graph is mocked or bypassed.
- Verifies graph wiring, invoke_llm helper, checkpointer hookup, and graceful
  LLM-disabled path.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from agents.base.agent import TDAgentBase

# ── Concrete subclass helpers ──────────────────────────────────────────────────


class MinimalAgent(TDAgentBase):
    """Agent with no SYSTEM_PROMPT and no tools — bare minimum."""

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        return {"agent_type": "minimal", "status": "ok"}


class PromptedAgent(TDAgentBase):
    """Agent with a SYSTEM_PROMPT but no tools."""

    SYSTEM_PROMPT = "You are a test agent. Be brief."

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        return {"agent_type": "prompted", "status": "ok"}


class TooledAgent(TDAgentBase):
    """Agent with a SYSTEM_PROMPT and a tool list."""

    SYSTEM_PROMPT = "You are a tool-using test agent."

    @staticmethod
    def _dummy_tool(x: int) -> int:
        """Returns x + 1."""
        return x + 1

    tools = [_dummy_tool]

    async def process_event(self, event_data: dict[str, Any]) -> dict[str, Any] | None:
        return {"agent_type": "tooled", "status": "ok"}


def _make_agent(cls, mock_redis, **kwargs):
    with patch("agents.base.agent.RedisClient", return_value=mock_redis):
        return cls(
            kwargs.get("agent_name", "TestAgent"),
            kwargs.get("input_q", "td:in"),
            kwargs.get("output_q", "td:out"),
        )


# ── graph property (no LLM key) ────────────────────────────────────────────────


def test_graph_returns_none_when_no_openai_key(mock_redis):
    """When OPENAI_API_KEY is empty the graph property returns None."""
    agent = _make_agent(MinimalAgent, mock_redis)
    with patch("agents.base.agent.settings") as mock_settings:
        mock_settings.openai_api_key = ""
        agent._graph = None  # Force rebuild
        result = agent._build_graph()
    assert result is None


def test_graph_builds_when_openai_key_present(mock_redis):
    """A compiled graph is returned when an API key is configured."""
    agent = _make_agent(PromptedAgent, mock_redis)
    with patch("agents.base.agent.settings") as mock_settings, patch(
        "agents.base.agent.ChatOpenAI"
    ) as mock_llm_cls:
        mock_settings.openai_api_key = "sk-test"
        mock_llm_cls.return_value = MagicMock()
        mock_llm_cls.return_value.bind_tools = MagicMock(
            return_value=MagicMock()
        )
        agent._graph = None
        built = agent._build_graph()
    assert built is not None


def test_graph_with_tools_builds(mock_redis):
    """Graph builds successfully when tools are provided."""
    agent = _make_agent(TooledAgent, mock_redis)
    with patch("agents.base.agent.settings") as mock_settings, patch(
        "agents.base.agent.ChatOpenAI"
    ) as mock_llm_cls:
        mock_settings.openai_api_key = "sk-test"
        mock_llm = MagicMock()
        mock_llm.bind_tools.return_value = mock_llm
        mock_llm_cls.return_value = mock_llm
        agent._graph = None
        built = agent._build_graph()
    assert built is not None


# ── invoke_llm helper ─────────────────────────────────────────────────────────


async def test_invoke_llm_returns_none_when_graph_is_none(mock_redis):
    """invoke_llm returns None gracefully when no graph is available."""
    agent = _make_agent(MinimalAgent, mock_redis)
    agent._graph = None
    with patch.object(type(agent), "graph", new_callable=lambda: property(lambda self: None)):
        result = await agent.invoke_llm({"trip_id": "T1"})
    assert result is None


async def test_invoke_llm_calls_graph_ainvoke(mock_redis):
    """invoke_llm calls graph.ainvoke with the correct thread_id config."""
    agent = _make_agent(PromptedAgent, mock_redis)

    fake_msg = MagicMock()
    fake_msg.content = "LLM reply"
    fake_graph = AsyncMock()
    fake_graph.ainvoke = AsyncMock(return_value={"messages": [fake_msg]})
    agent._graph = fake_graph

    result = await agent.invoke_llm({"trip_id": "TRIP-42"})

    assert result == "LLM reply"
    fake_graph.ainvoke.assert_awaited_once()
    call_config = fake_graph.ainvoke.call_args[1]["config"]
    assert call_config["configurable"]["thread_id"] == "TRIP-42"


async def test_invoke_llm_uses_explicit_thread_id(mock_redis):
    """invoke_llm uses the provided thread_id rather than the event's trip_id."""
    agent = _make_agent(PromptedAgent, mock_redis)

    fake_msg = MagicMock()
    fake_msg.content = "reply"
    fake_graph = AsyncMock()
    fake_graph.ainvoke = AsyncMock(return_value={"messages": [fake_msg]})
    agent._graph = fake_graph

    await agent.invoke_llm({"trip_id": "TRIP-42"}, thread_id="custom-thread")

    call_config = fake_graph.ainvoke.call_args[1]["config"]
    assert call_config["configurable"]["thread_id"] == "custom-thread"


async def test_invoke_llm_handles_list_content(mock_redis):
    """When the LLM returns a list-of-blocks, invoke_llm joins text blocks."""
    agent = _make_agent(PromptedAgent, mock_redis)

    fake_msg = MagicMock()
    fake_msg.content = [
        {"type": "text", "text": "Hello "},
        {"type": "text", "text": "World"},
        {"type": "tool_use", "id": "call_1"},
    ]
    fake_graph = AsyncMock()
    fake_graph.ainvoke = AsyncMock(return_value={"messages": [fake_msg]})
    agent._graph = fake_graph

    result = await agent.invoke_llm({"trip_id": "T1"})
    assert result == "Hello World"


# ── _format_event helper ──────────────────────────────────────────────────────


def test_format_event_serializes_to_json(mock_redis):
    """_format_event produces valid JSON from the event dict."""
    import json

    agent = _make_agent(MinimalAgent, mock_redis)
    event = {"trip_id": "T1", "event_type": "harsh_brake"}
    raw = agent._format_event(event)
    parsed = json.loads(raw)
    assert parsed["trip_id"] == "T1"


# ── _get_checkpointer ─────────────────────────────────────────────────────────


def test_default_checkpointer_is_memory_saver(mock_redis):
    """Default checkpointer is MemorySaver — no external dependency."""
    from langgraph.checkpoint.memory import MemorySaver

    agent = _make_agent(MinimalAgent, mock_redis)
    assert isinstance(agent._get_checkpointer(), MemorySaver)


def test_checkpointer_can_be_overridden(mock_redis):
    """Subclasses can inject a custom checkpointer."""
    from langgraph.checkpoint.memory import MemorySaver

    custom_checkpointer = MemorySaver()

    class CustomCheckpointAgent(MinimalAgent):
        def _get_checkpointer(self):
            return custom_checkpointer

    agent = _make_agent(CustomCheckpointAgent, mock_redis)
    assert agent._get_checkpointer() is custom_checkpointer


# ── SYSTEM_PROMPT prepending ──────────────────────────────────────────────────


async def test_system_prompt_prepended_when_no_system_message(mock_redis):
    """
    When SYSTEM_PROMPT is set the chatbot node injects it as a SystemMessage
    before the first user message.
    """
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    captured_messages: list = []

    class CapturingAgent(TDAgentBase):
        SYSTEM_PROMPT = "System instruction."

        async def process_event(self, event_data):
            return None

    agent = _make_agent(CapturingAgent, mock_redis)

    def _fake_llm_invoke(messages):
        captured_messages.extend(messages)
        return AIMessage(content="ok")

    fake_llm = MagicMock()
    fake_llm.bind_tools = MagicMock(return_value=fake_llm)
    fake_llm.invoke = _fake_llm_invoke

    with patch("agents.base.agent.settings") as mock_settings, patch(
        "agents.base.agent.ChatOpenAI", return_value=fake_llm
    ):
        mock_settings.openai_api_key = "sk-test"
        agent._graph = None
        graph = agent._build_graph()

    await graph.ainvoke(
        {"messages": [HumanMessage(content="hello")]},
        config={"configurable": {"thread_id": "t1"}},
    )

    assert any(isinstance(m, SystemMessage) for m in captured_messages)
    system_msgs = [m for m in captured_messages if isinstance(m, SystemMessage)]
    assert system_msgs[0].content == "System instruction."


# ── Specialist agent class attributes ─────────────────────────────────────────


def test_safety_agent_has_system_prompt():
    from agents.safety.agent import SafetyAgent

    assert SafetyAgent.SYSTEM_PROMPT != ""
    assert "safety" in SafetyAgent.SYSTEM_PROMPT.lower()


def test_scoring_agent_has_system_prompt():
    from agents.scoring.agent import ScoringAgent

    assert ScoringAgent.SYSTEM_PROMPT != ""
    assert "score" in ScoringAgent.SYSTEM_PROMPT.lower()


def test_sentiment_agent_has_system_prompt():
    from agents.sentiment.agent import SentimentAgent

    assert SentimentAgent.SYSTEM_PROMPT != ""
    assert "sentiment" in SentimentAgent.SYSTEM_PROMPT.lower()


def test_support_agent_has_system_prompt():
    from agents.driver_support.agent import SupportAgent

    assert SupportAgent.SYSTEM_PROMPT != ""
    assert "coach" in SupportAgent.SYSTEM_PROMPT.lower()


# ── process_event still works without LLM ────────────────────────────────────


async def test_safety_process_event_without_llm(mock_redis):
    """SafetyAgent.process_event returns a result even without LLM configured."""
    from agents.safety.agent import SafetyAgent

    with patch("agents.base.agent.RedisClient", return_value=mock_redis):
        agent = SafetyAgent("SafetyAgent", "in", "out")

    agent._graph = None
    with patch.object(type(agent), "graph", new_callable=lambda: property(lambda self: None)):
        result = await agent.process_event({"event": {"event_id": "E1", "trip_id": "T1", "event_type": "harsh_brake"}})

    assert result is not None
    assert result["agent_type"] == "safety"
    assert "analysis" not in result  # no LLM → no analysis key


async def test_scoring_process_event_without_llm(mock_redis):
    """ScoringAgent.process_event returns a result even without LLM configured."""
    from agents.scoring.agent import ScoringAgent

    with patch("agents.base.agent.RedisClient", return_value=mock_redis):
        agent = ScoringAgent("ScoringAgent", "in", "out")

    agent._graph = None
    with patch.object(type(agent), "graph", new_callable=lambda: property(lambda self: None)):
        result = await agent.process_event({"event": {"event_id": "E2", "trip_id": "T2", "event_type": "end_of_trip"}})

    assert result is not None
    assert result["agent_type"] == "scoring"
    assert result["score"] == 85
