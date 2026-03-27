"""
Tests for TDAgentBase lifecycle.

Strategy: inject a mock RedisClient instead of creating a real one.
We patch `agents.base.agent.RedisClient` so constructing any TDAgentBase
subclass uses our mock automatically.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, patch

from agents.base.agent import TDAgentBase

# ── Concrete subclass for testing ─────────────────────────────────────────────


class EchoAgent(TDAgentBase):
    """Minimal agent that echoes the event back as its result."""

    async def process_event(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        return {"echoed": True, "trip_id": event_data.get("trip_id")}


class NullAgent(TDAgentBase):
    """Agent that returns None — should NOT push to the output queue."""

    async def process_event(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None


class ErrorAgent(TDAgentBase):
    """Agent whose process_event raises an exception — run() should survive."""

    async def process_event(
        self, event_data: dict[str, Any]
    ) -> dict[str, Any] | None:
        raise RuntimeError("Simulated processing error")


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_agent(
    cls, mock_redis, agent_name="TestAgent", input_q="td:in", output_q="td:out"
):
    """
    Build an agent with a pre-injected mock redis.
    Patches RedisClient at the module level so __init__ gets the mock.
    """
    with patch("agents.base.agent.RedisClient", return_value=mock_redis):
        agent = cls(agent_name, input_q, output_q)
    return agent


async def _run_once(agent, mock_redis, event_json: str):
    """
    Drive the agent's run() loop for exactly one productive iteration:
      - First pop → returns the event
      - Second pop → returns None (triggers stop)
    """
    call_count = 0

    async def _pop_side_effect(queue, timeout=0):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return event_json
        agent.stop()
        return None

    mock_redis.pop = AsyncMock(side_effect=_pop_side_effect)
    await agent.run()


# ── Tests ──────────────────────────────────────────────────────────────────────


async def test_run_processes_single_event(mock_redis, telemetry_packet_json):
    """process_event is called exactly once per received event."""
    agent = _make_agent(EchoAgent, mock_redis)
    await _run_once(agent, mock_redis, telemetry_packet_json)
    # Push was called once with the echoed result
    mock_redis.push.assert_called_once()


async def test_run_publishes_result_to_output_queue(mock_redis, telemetry_packet_json):
    """The result is pushed to the configured output queue."""
    agent = _make_agent(EchoAgent, mock_redis, output_q="td:results")
    await _run_once(agent, mock_redis, telemetry_packet_json)
    call_args = mock_redis.push.call_args[0]
    assert call_args[0] == "td:results"


async def test_run_result_enriched_with_source_agent(mock_redis, telemetry_packet_json):
    """Result dict always carries source_agent = agent_name."""
    agent = _make_agent(EchoAgent, mock_redis, agent_name="EchoAgent")
    await _run_once(agent, mock_redis, telemetry_packet_json)
    published_raw = mock_redis.push.call_args[0][1]
    published = json.loads(published_raw)
    assert published["source_agent"] == "EchoAgent"


async def test_run_skips_push_when_process_returns_none(
    mock_redis, telemetry_packet_json
):
    """If process_event returns None, no push is made."""
    agent = _make_agent(NullAgent, mock_redis)
    await _run_once(agent, mock_redis, telemetry_packet_json)
    mock_redis.push.assert_not_called()


async def test_run_handles_invalid_json(mock_redis):
    """Bad JSON from Redis is caught; run() does not raise."""
    agent = _make_agent(EchoAgent, mock_redis)

    call_count = 0

    async def _pop_side_effect(queue, timeout=0):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return "THIS IS NOT JSON {{{"
        agent.stop()
        return None

    mock_redis.pop = AsyncMock(side_effect=_pop_side_effect)
    await agent.run()  # Must not raise
    mock_redis.push.assert_not_called()


async def test_run_handles_process_event_exception(mock_redis, telemetry_packet_json):
    """process_event raising an exception does not crash run()."""
    agent = _make_agent(ErrorAgent, mock_redis)
    await _run_once(agent, mock_redis, telemetry_packet_json)
    # No push should happen
    mock_redis.push.assert_not_called()


async def test_run_skips_empty_pop(mock_redis):
    """timeout pop returning None does not trigger process_event or push."""
    agent = _make_agent(EchoAgent, mock_redis)
    call_count = 0

    async def _pop_side_effect(queue, timeout=0):
        nonlocal call_count
        call_count += 1
        if call_count >= 3:
            agent.stop()
        return None  # Always empty

    mock_redis.pop = AsyncMock(side_effect=_pop_side_effect)
    await agent.run()
    mock_redis.push.assert_not_called()


async def test_stop_terminates_run(mock_redis):
    """agent.stop() causes run() to exit without hanging."""
    agent = _make_agent(EchoAgent, mock_redis)
    call_count = 0

    async def _pop_side_effect(queue, timeout=0):
        nonlocal call_count
        call_count += 1
        agent.stop()  # Stop on first poll
        return None

    mock_redis.pop = AsyncMock(side_effect=_pop_side_effect)
    await agent.run()  # Must return, not loop forever
    assert call_count >= 1


async def test_close_called_on_shutdown(mock_redis, telemetry_packet_json):
    """redis.close() is called when run() exits."""
    agent = _make_agent(EchoAgent, mock_redis)
    await _run_once(agent, mock_redis, telemetry_packet_json)
    mock_redis.close.assert_called_once()
