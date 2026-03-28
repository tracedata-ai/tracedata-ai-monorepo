"""
Tests for OrchestratorAgent event routing via EVENT_MAP and Celery dispatch.

Verifies that TripEvent payloads are correctly routed to specialized agent workers
via Celery tasks using the centralized EVENT_MAP.
"""

from unittest.mock import MagicMock, patch

import pytest

from agents.orchestrator.agent import EVENT_MAP, OrchestratorAgent


class TestEventMap:
    """Tests for EVENT_MAP completeness and correctness."""

    def test_event_map_covers_all_safety_events(self):
        """EVENT_MAP includes all safety event types."""
        safety_events = {
            "collision",
            "rollover",
            "driver_sos",
            "harsh_brake",
            "hard_accel",
            "harsh_corner",
        }
        for event_type in safety_events:
            assert event_type in EVENT_MAP
            assert EVENT_MAP[event_type]["agent"] == "safety"
            assert EVENT_MAP[event_type]["task"] == "tasks.safety_tasks.analyse_event"

    def test_event_map_covers_all_scoring_events(self):
        """EVENT_MAP includes all scoring event types."""
        scoring_events = {"end_of_trip"}
        for event_type in scoring_events:
            assert event_type in EVENT_MAP
            assert EVENT_MAP[event_type]["agent"] == "scoring"
            assert EVENT_MAP[event_type]["task"] == "tasks.scoring_tasks.score_trip"

    def test_event_map_covers_all_sentiment_events(self):
        """EVENT_MAP includes all sentiment event types."""
        sentiment_events = {
            "driver_dispute",
            "driver_complaint",
            "driver_feedback",
            "driver_comment",
        }
        for event_type in sentiment_events:
            assert event_type in EVENT_MAP
            assert EVENT_MAP[event_type]["agent"] == "sentiment"
            assert (
                EVENT_MAP[event_type]["task"]
                == "tasks.sentiment_tasks.analyse_feedback"
            )

    def test_event_map_has_required_fields(self):
        """Each EVENT_MAP entry has 'agent' and 'task' fields."""
        for event_type, route in EVENT_MAP.items():
            assert "agent" in route, f"{event_type} missing 'agent' field"
            assert "task" in route, f"{event_type} missing 'task' field"
            assert isinstance(route["agent"], str)
            assert isinstance(route["task"], str)


class TestAgentForEvent:
    """Tests for _agent_for_event routing logic."""

    @pytest.mark.parametrize("event_type", ["collision", "rollover", "harsh_brake"])
    def test_safety_events_map_to_safety_agent(self, event_type):
        """Safety event types route to 'safety' agent."""
        assert OrchestratorAgent._agent_for_event(event_type) == "safety"

    def test_end_of_trip_maps_to_scoring_agent(self):
        """end_of_trip event routes to 'scoring' agent."""
        assert OrchestratorAgent._agent_for_event("end_of_trip") == "scoring"

    @pytest.mark.parametrize(
        "event_type", ["driver_dispute", "driver_complaint", "driver_feedback"]
    )
    def test_sentiment_events_map_to_sentiment_agent(self, event_type):
        """Sentiment event types route to 'sentiment' agent."""
        assert OrchestratorAgent._agent_for_event(event_type) == "sentiment"

    def test_unknown_event_defaults_to_orchestrator(self):
        """Unknown event types default to 'orchestrator' agent."""
        assert OrchestratorAgent._agent_for_event("unknown_event") == "orchestrator"
        assert OrchestratorAgent._agent_for_event("smoothness_log") == "orchestrator"


class TestDispatchRouting:
    """Tests for _dispatch method and Celery queue selection."""

    def _make_agent(self, mock_redis, mock_db, mock_celery):
        """Create OrchestratorAgent with mocked dependencies."""
        with (
            patch("agents.orchestrator.agent.RedisClient", return_value=mock_redis),
            patch("agents.orchestrator.agent.DBManager", return_value=mock_db),
            patch("agents.orchestrator.agent._get_celery", return_value=mock_celery),
        ):
            agent = OrchestratorAgent(truck_ids=["truck1"])
        return agent

    @pytest.mark.asyncio
    async def test_safety_event_sends_to_safety_queue(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        """A collision event dispatches to safety queue."""
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "collision"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        capsule = agent._seal_capsule(trip_event)

        # Mock the capsule as dict
        capsule_dict = {k: v for k, v in capsule.__dict__.items()}
        capsule.model_dump = MagicMock(return_value=capsule_dict)

        ctx = {"trip_id": "test_trip", "action": "test"}
        result = await agent._dispatch(trip_event, capsule, ctx)

        assert result is True
        mock_celery.send_task.assert_called_once()
        call_args = mock_celery.send_task.call_args
        assert call_args[0][0] == "tasks.safety_tasks.analyse_event"

    @pytest.mark.asyncio
    async def test_unknown_event_type_not_dispatched(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        """An unknown event type is not dispatched to any queue."""
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "lane_change"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        capsule = agent._seal_capsule(trip_event)
        capsule.model_dump = MagicMock(return_value={})

        ctx = {"trip_id": "test_trip", "action": "test"}
        result = await agent._dispatch(trip_event, capsule, ctx)

        assert result is False
        mock_celery.send_task.assert_not_called()
        mock_db.release_lock.assert_called_once()

    @pytest.mark.asyncio
    async def test_dispatch_includes_event_data_in_payload(
        self, mock_redis, mock_db, mock_celery, telemetry_packet
    ):
        """Dispatch payload includes both IntentCapsule and flat event data."""
        agent = self._make_agent(mock_redis, mock_db, mock_celery)
        event = telemetry_packet["event"]
        event["event_type"] = "harsh_brake"

        from common.models.events import TripEvent

        trip_event = TripEvent(**event)
        capsule = agent._seal_capsule(trip_event)

        capsule_dict = {"trip_id": trip_event.trip_id, "agent": "safety"}
        capsule.model_dump = MagicMock(return_value=capsule_dict)

        ctx = {"trip_id": trip_event.trip_id, "action": "test"}
        result = await agent._dispatch(trip_event, capsule, ctx)

        assert result is True
        mock_celery.send_task.assert_called_once()
        call_kwargs = mock_celery.send_task.call_args[1]
        payload = call_kwargs["kwargs"]["intent_capsule"]
        assert "event_type" in payload
        assert "event_data" in payload
        assert payload["event_type"] == "harsh_brake"

    @pytest.mark.parametrize(
        "event_type,expected_queue",
        [
            ("collision", "td:agent:safety"),
            ("end_of_trip", "td:agent:scoring"),
            ("driver_dispute", "td:agent:sentiment"),
        ],
    )
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
        """Events dispatch to the correct target queue."""
        # Mock settings to return predictable queue names
        with patch("agents.orchestrator.agent.settings") as mock_settings:
            mock_settings.safety_queue = "td:agent:safety"
            mock_settings.scoring_queue = "td:agent:scoring"
            mock_settings.sentiment_queue = "td:agent:sentiment"

            agent = self._make_agent(mock_redis, mock_db, mock_celery)
            event = telemetry_packet["event"]
            event["event_type"] = event_type

            from common.models.events import TripEvent

            trip_event = TripEvent(**event)
            capsule = agent._seal_capsule(trip_event)
            capsule.model_dump = MagicMock(return_value={})

            ctx = {"trip_id": trip_event.trip_id, "action": "test"}
            result = await agent._dispatch(trip_event, capsule, ctx)

            assert result is True
            mock_celery.send_task.assert_called_once()
            call_kwargs = mock_celery.send_task.call_args[1]
            assert call_kwargs["queue"] == expected_queue


class TestInitialization:
    """Tests for OrchestratorAgent initialization."""

    def test_init_with_truck_ids(self):
        """OrchestratorAgent initializes with truck_ids only."""
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
        ):
            agent = OrchestratorAgent(truck_ids=["truck1", "truck2"])
            assert agent.truck_ids == ["truck1", "truck2"]

    def test_init_with_no_truck_ids(self):
        """OrchestratorAgent initializes with empty truck_ids if not provided."""
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
        ):
            agent = OrchestratorAgent()
            assert agent.truck_ids == []

    def test_legacy_parameters_not_accepted(self):
        """OrchestratorAgent does not accept legacy agent_name/input_queue parameters."""
        with (
            patch("agents.orchestrator.agent.RedisClient"),
            patch("agents.orchestrator.agent.DBManager"),
        ):
            # New interface should not accept agent_name, input_queue, output_queue
            agent = OrchestratorAgent(truck_ids=["truck1"])  # Correct usage
            assert agent.truck_ids == ["truck1"]
            assert not hasattr(agent, "_legacy_mode")
