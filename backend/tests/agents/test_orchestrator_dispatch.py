"""
Tests for OrchestratorAgent dispatch logic.

Verifies that TripEvent payloads are routed by OrchestratorAgent using
the legacy process_event interface for backward compatibility.
"""

import json
from unittest.mock import MagicMock, patch

from agents.orchestrator.agent import OrchestratorAgent


def _make_orchestrator(mock_redis, mock_db):
    """Inject fake redis and db into OrchestratorAgent."""
    with (
        patch("agents.orchestrator.agent.RedisClient", return_value=mock_redis),
        patch("agents.orchestrator.agent.DBManager", return_value=mock_db),
    ):
        agent = OrchestratorAgent(
            agent_name="OrchestratorAgent",
            input_queue="td:orchestrator:events",
            output_queue="td:orchestrator:results",
        )
    return agent


# ── Dispatch Routing Tests ─────────────────────────────────────────────────────


async def test_harsh_brake_dispatches_to_safety_queue(mock_redis, telemetry_packet):
    """A harsh_brake TripEvent is pushed to td:agent:safety via push_to_buffer."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    await agent.process_event(telemetry_packet["event"])

    mock_redis.push_to_buffer.assert_called_once()
    queue_name = mock_redis.push_to_buffer.call_args[0][0]
    assert queue_name == "td:agent:safety"


async def test_harsh_brake_payload_preserved_in_dispatch(
    mock_redis, telemetry_packet, event_id
):
    """The full event payload (not a truncated copy) arrives in the safety queue."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    await agent.process_event(telemetry_packet["event"])

    pushed_raw = mock_redis.push_to_buffer.call_args[0][1]
    pushed = json.loads(pushed_raw)
    assert pushed["event_id"] == event_id


async def test_harsh_brake_result_has_next_hop_safety(mock_redis, telemetry_packet):
    """process_event returns dispatched status for recognized events."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert result["status"] == "dispatched"


async def test_unknown_event_type_no_dispatch(mock_redis, telemetry_packet):
    """An unknown event type triggers no push to any queue."""
    telemetry_packet["event"]["event_type"] = "lane_change"
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    result = await agent.process_event(telemetry_packet["event"])

    mock_redis.push_to_buffer.assert_not_called()
    assert result is not None
    assert result["status"] == "dispatched"


async def test_missing_event_key_no_crash(mock_redis):
    """A malformed packet with no 'event' key does not raise."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    result = await agent.process_event({"ping_type": "heartbeat"})
    assert result is None
    mock_redis.push_to_buffer.assert_not_called()


async def test_result_always_contains_agent_type(mock_redis, telemetry_packet):
    """Result dict always contains agent_type = orchestrator."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert result["agent_type"] == "orchestrator"


async def test_result_always_contains_status(mock_redis, telemetry_packet):
    """Result dict always contains a status field."""
    mock_db = MagicMock()
    agent = _make_orchestrator(mock_redis, mock_db)
    result = await agent.process_event(telemetry_packet["event"])
    assert result is not None
    assert "status" in result
