"""
Tests for OrchestratorAgent dispatch logic.

Verifies that harsh_brake events are routed to the safety queue,
and that unknown event types produce no dispatch.
"""

import json
from unittest.mock import patch

from agents.worker import OrchestratorAgent


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
    """A harsh_brake TelemetryPacket is pushed to td:agent:safety."""
    agent = _make_orchestrator(mock_redis)
    await agent.process_event(telemetry_packet)

    # push should have been called once with the safety queue
    mock_redis.push.assert_called_once()
    queue_name = mock_redis.push.call_args[0][0]
    assert queue_name == "td:agent:safety"


async def test_harsh_brake_payload_preserved_in_dispatch(
    mock_redis, telemetry_packet, event_id
):
    """The full event payload (not a truncated copy) arrives in the safety queue."""
    agent = _make_orchestrator(mock_redis)
    await agent.process_event(telemetry_packet)

    pushed_raw = mock_redis.push.call_args[0][1]
    pushed = json.loads(pushed_raw)
    assert pushed["event"]["event_id"] == event_id


async def test_harsh_brake_result_has_next_hop_safety(mock_redis, telemetry_packet):
    """process_event returns next_hop: safety for harsh_brake events."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet)
    assert result["next_hop"] == "safety"


async def test_unknown_event_type_no_dispatch(mock_redis, telemetry_packet):
    """An unknown event type triggers no push to any queue."""
    telemetry_packet["event"]["event_type"] = "lane_change"
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet)

    mock_redis.push.assert_not_called()
    assert result["next_hop"] == "none"


async def test_missing_event_key_no_crash(mock_redis):
    """A malformed packet with no 'event' key does not raise."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event({"ping_type": "heartbeat"})
    assert result["agent_type"] == "orchestrator"
    mock_redis.push.assert_not_called()


async def test_result_always_contains_agent_type(mock_redis, telemetry_packet):
    """Result dict always contains agent_type = orchestrator."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet)
    assert result["agent_type"] == "orchestrator"


async def test_result_always_contains_status(mock_redis, telemetry_packet):
    """Result dict always contains a status field."""
    agent = _make_orchestrator(mock_redis)
    result = await agent.process_event(telemetry_packet)
    assert "status" in result
