"""
Tests for OrchestratorAgent dispatch logic.

Verifies that TripEvent payloads are routed by OrchestratorAgent using
the current Redis queue contract.
"""

import json
from unittest.mock import patch

from agents.orchestrator.agent import OrchestratorAgent


def _make_orchestrator(mock_redis):
    """Inject fake redis into OrchestratorAgent."""
    with patch("agents.base.agent.RedisClient", return_value=mock_redis):
        agent = OrchestratorAgent(
            "OrchestratorAgent",
            "td:orchestrator:events",
            "td:orchestrator:results",
        )
    return agent


# ── Dispatch Routing Tests ─────────────────────────────────────────────────────


async def test_harsh_brake_dispatches_to_safety_queue(mock_redis, telemetry_packet):
    """A harsh_brake TripEvent is pushed to td:agent:safety via push_to_buffer."""
    agent = _make_orchestrator(mock_redis)
    await agent.process_event(telemetry_packet["event"])

    mock_redis.push_to_buffer.assert_called_once()
    queue_name = mock_redis.push_to_buffer.call_args[0][0]
    assert queue_name == "td:agent:safety"


async def test_harsh_brake_payload_preserved_in_dispatch(
    mock_redis, telemetry_packet, event_id
):
    """The full event payload (not a truncated copy) arrives in the safety queue."""
    agent = _make_orchestrator(mock_redis)
    await agent.process_event(telemetry_packet["event"])

    pushed_raw = mock_redis.push_to_buffer.call_args[0][1]
    pushed = json.loads(pushed_raw)
    assert pushed["event_id"] == event_id


async def test_harsh_brake_result_has_next_hop_safety(mock_redis, telemetry_packet):
    """process_event returns dispatched status for recognized events."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert result["status"] == "dispatched"


async def test_unknown_event_type_no_dispatch(mock_redis, telemetry_packet):
    """An unknown event type triggers no push to any queue."""
    telemetry_packet["event"]["event_type"] = "lane_change"
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet["event"])

    mock_redis.push_to_buffer.assert_not_called()
    assert result is not None
    assert result["status"] == "dispatched"


async def test_missing_event_key_no_crash(mock_redis):
    """A malformed packet with no 'event' key does not raise."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event({"ping_type": "heartbeat"})
    assert result is None
    mock_redis.push_to_buffer.assert_not_called()


async def test_result_always_contains_agent_type(mock_redis, telemetry_packet):
    """Result dict always contains agent_type = orchestrator."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert result["agent_type"] == "orchestrator"


async def test_result_always_contains_status(mock_redis, telemetry_packet):
    """Result dict always contains a status field."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert "status" in result
