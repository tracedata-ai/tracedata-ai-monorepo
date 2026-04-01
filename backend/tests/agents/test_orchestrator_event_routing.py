"""
Tests for OrchestratorAgent — LLM + EventMatrix routing and Celery dispatch.

Static EVENT_MAP was removed; routing uses the LLM and tools. Dispatch still
maps agent names to Celery queues/tasks.
"""

from unittest.mock import MagicMock, patch

import pytest

from agents.orchestrator import agent as orchestrator_module
from agents.orchestrator.agent import OrchestratorAgent


class TestLLMRoutingArchitecture:
    """Routing is dynamic; there is no module-level EVENT_MAP."""

    def test_no_event_map_constant(self):
        assert not hasattr(orchestrator_module, "EVENT_MAP")


class TestDeprecatedAgentForEvent:
    """_agent_for_event is deprecated and always returns orchestrator."""

    @pytest.mark.parametrize(
        "event_type",
        [
            "collision",
            "rollover",
            "harsh_brake",
            "end_of_trip",
            "driver_dispute",
            "unknown_event",
            "smoothness_log",
        ],
    )
    def test_returns_orchestrator(self, event_type):
        assert OrchestratorAgent._agent_for_event(event_type) == "orchestrator"


class TestDispatchRouting:
    """_dispatch shape: capsules dict + routing_decision from LLM path."""

    def _make_agent(self, mock_redis, mock_db, mock_celery):
        with (
            patch("agents.orchestrator.agent.RedisClient", return_value=mock_redis),
            patch("agents.orchestrator.agent.DBManager", return_value=mock_db),
            patch("agents.orchestrator.agent._get_celery", return_value=mock_celery),
            patch("agents.orchestrator.agent._get_llm", return_value=MagicMock()),
        ):
            agent = OrchestratorAgent(truck_ids=["truck1"])
        return agent

    @pytest.mark.skip(reason="Requires running Redis server - Celery integration test")
    @pytest.mark.asyncio
    async def test_safety_event_sends_to_safety_queue(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "collision"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        capsule = agent._seal_capsule(trip_event, "safety")
        capsules = {"safety": capsule}
        ctx = {"trip_id": "test_trip", "action": "test"}
        routing_decision = {"agents_to_dispatch": ["safety"], "action": "test"}
        result = await agent._dispatch(trip_event, capsules, ctx, routing_decision)

        assert result is True
        mock_celery.send_task.assert_called_once()
        call_args = mock_celery.send_task.call_args
        assert call_args[0][0] == "tasks.safety_tasks.analyse_event"

    @pytest.mark.skip(reason="Requires running Redis server - Celery integration test")
    @pytest.mark.asyncio
    async def test_unknown_event_type_not_dispatched(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "lane_change"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        routing_decision = {"agents_to_dispatch": [], "action": "none"}
        result = await agent._dispatch(trip_event, {}, {}, routing_decision)

        assert result is False
        mock_celery.send_task.assert_not_called()
        mock_db.release_lock.assert_called_once()

    @pytest.mark.skip(reason="Requires running Redis server - Celery integration test")
    @pytest.mark.asyncio
    async def test_dispatch_includes_event_data_in_payload(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "harsh_brake"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        capsule = agent._seal_capsule(trip_event, "safety")
        capsules = {"safety": capsule}
        ctx = {"trip_id": trip_event.trip_id, "action": "test"}
        routing_decision = {"agents_to_dispatch": ["safety"], "action": "test"}
        result = await agent._dispatch(trip_event, capsules, ctx, routing_decision)

        assert result is True
        mock_celery.send_task.assert_called_once()
        call_kwargs = mock_celery.send_task.call_args[1]
        payload = call_kwargs["kwargs"]["intent_capsule"]
        assert payload["agent"] == "safety"
        assert payload["trip_id"] == trip_event.trip_id
        assert payload["device_event_id"] == trip_event.device_event_id

    @pytest.mark.parametrize(
        "event_type,expected_queue",
        [
            ("collision", "td:agent:safety"),
            ("end_of_trip", "td:agent:scoring"),
            ("driver_dispute", "td:agent:sentiment"),
        ],
    )
    @pytest.mark.skip(reason="Requires running Redis server - Celery integration test")
    @pytest.mark.asyncio
    async def test_dispatch_to_correct_queue(
        self,
        event_type,
        expected_queue,
        mock_redis,
        mock_db,
        mock_celery,
        telemetry_packet,
    ):
        agent_map = {
            "collision": "safety",
            "end_of_trip": "scoring",
            "driver_dispute": "sentiment",
        }
        agent_name = agent_map[event_type]
        with patch("agents.orchestrator.agent.settings") as mock_settings:
            mock_settings.safety_queue = "td:agent:safety"
            mock_settings.scoring_queue = "td:agent:scoring"
            mock_settings.sentiment_queue = "td:agent:sentiment"

            agent = self._make_agent(mock_redis, mock_db, mock_celery)
            event = telemetry_packet["event"]
            event["event_type"] = event_type

            from common.models.events import TripEvent

            trip_event = TripEvent(**event)
            capsule = agent._seal_capsule(trip_event, agent_name)
            capsules = {agent_name: capsule}
            ctx = {"trip_id": trip_event.trip_id, "action": "test"}
            routing_decision = {
                "agents_to_dispatch": [agent_name],
                "action": "test",
            }
            result = await agent._dispatch(trip_event, capsules, ctx, routing_decision)

            assert result is True
            mock_celery.send_task.assert_called_once()
            call_kwargs = mock_celery.send_task.call_args[1]
            assert call_kwargs["queue"] == expected_queue


class TestInitialization:
    """OrchestratorAgent initialization."""

    def test_init_with_truck_ids(self):
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
            patch("agents.orchestrator.agent._get_llm", return_value=MagicMock()),
        ):
            agent = OrchestratorAgent(truck_ids=["truck1", "truck2"])
            assert agent.truck_ids == ["truck1", "truck2"]

    def test_init_with_no_truck_ids(self):
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
            patch("agents.orchestrator.agent._get_llm", return_value=MagicMock()),
        ):
            agent = OrchestratorAgent()
            assert agent.truck_ids == []

    def test_legacy_parameters_not_accepted(self):
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
            patch("agents.orchestrator.agent._get_llm", return_value=MagicMock()),
        ):
            agent = OrchestratorAgent(truck_ids=["truck1"])
            assert agent.truck_ids == ["truck1"]
            assert not hasattr(agent, "_legacy_mode")
