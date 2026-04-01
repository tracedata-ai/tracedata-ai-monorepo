"""
Unit tests for cache warming strategy.

Tests for:
- Event-driven warming (Safety Agent)
- Aggregation-driven warming (Scoring Agent)
- Redis schema consistency
- Cache warming helper functions
"""

from unittest.mock import AsyncMock

import pytest

from common.config.events import (
    get_agents_to_dispatch,
    get_cache_requirements,
    get_event_config,
    get_warming_type,
)
from common.redis.keys import RedisSchema

# ──────────────────────────────────────────────────────────────────────────────
# Test EventMatrix helpers
# ──────────────────────────────────────────────────────────────────────────────


class TestEventMatrixHelpers:
    """Tests for EventMatrix configuration helpers."""

    def test_get_event_config_harsh_brake(self):
        """Test getting config for harsh_brake event."""
        config = get_event_config("harsh_brake")

        assert config is not None
        assert config["event_type"] == "harsh_brake"
        assert config["category"] == "harsh_events"
        assert config["ml_weight"] == 0.7
        assert "agents_from_action" in config
        assert len(config["agents_from_action"]) > 0

    def test_get_event_config_nonexistent(self):
        """Test getting config for nonexistent event returns None."""
        config = get_event_config("nonexistent_event")
        assert config is None

    def test_get_agents_to_dispatch_harsh_brake(self):
        """Test getting agents for harsh_brake event."""
        agents = get_agents_to_dispatch("harsh_brake")
        assert isinstance(agents, list)
        assert len(agents) > 0
        assert "scoring" in agents

    def test_get_agents_to_dispatch_safety_event(self):
        """Test getting agents for safety-critical event."""
        agents = get_agents_to_dispatch("collision")
        assert "safety" in agents

    def test_get_agents_to_dispatch_no_agents(self):
        """Test events that don't dispatch agents."""
        agents = get_agents_to_dispatch("normal_operation")
        assert agents == []

    def test_get_warming_type_event_driven(self):
        """Test event-driven warming detection."""
        warming_type = get_warming_type("harsh_brake")
        assert warming_type == "event-driven"

    def test_get_warming_type_aggregation_driven(self):
        """Test aggregation-driven warming detection."""
        warming_type = get_warming_type("end_of_trip")
        assert warming_type == "aggregation-driven"

    def test_get_warming_type_safety_critical(self):
        """Test safety-critical events use event-driven warming."""
        warming_type = get_warming_type("collision")
        assert warming_type == "event-driven"

    def test_get_cache_requirements_event_driven(self):
        """Test cache requirements for event-driven warming."""
        reqs = get_cache_requirements("harsh_brake", "scoring")
        assert reqs["needs"] == ["current_event", "trip_context"]
        assert reqs["ttl"] == 300  # 5 minutes

    def test_get_cache_requirements_aggregation_scoring(self):
        """Test cache requirements for aggregation-driven scoring."""
        reqs = get_cache_requirements("end_of_trip", "scoring")
        assert "all_pings" in reqs["needs"]
        assert "historical_avg" in reqs["needs"]
        assert reqs["ttl"] == 3600  # 1 hour

    def test_get_cache_requirements_aggregation_support(self):
        """Test cache requirements for aggregation-driven support."""
        reqs = get_cache_requirements("end_of_trip", "support")
        assert "trip_context" in reqs["needs"]
        assert "coaching_history" in reqs["needs"]
        assert reqs["ttl"] == 3600  # 1 hour


# ──────────────────────────────────────────────────────────────────────────────
# Test Redis Schema patterns
# ──────────────────────────────────────────────────────────────────────────────


class TestRedisSchemaPatterns:
    """Tests for Redis key schema consistency."""

    def test_agent_data_key_format(self):
        """Test agent data key format."""
        key = RedisSchema.Trip.agent_data("TRP-123", "safety", "current_event")
        assert key == "trips:TRP-123:safety:current_event"

    def test_event_driven_cache_keys(self):
        """Test event-driven cache keys."""
        keys = RedisSchema.Trip.event_driven_cache("TRP-456", "safety")
        assert "current_event" in keys
        assert "trip_context" in keys
        assert "trips:TRP-456:safety:current_event" in keys.values()
        assert "trips:TRP-456:safety:trip_context" in keys.values()

    def test_aggregation_driven_cache_keys(self):
        """Test aggregation-driven cache keys."""
        keys = RedisSchema.Trip.aggregation_driven_cache("TRP-789", "scoring")
        assert "all_pings" in keys
        assert "historical_avg" in keys
        assert "trips:TRP-789:scoring:all_pings" in keys.values()
        assert "trips:TRP-789:scoring:historical_avg" in keys.values()

    def test_lock_keys(self):
        """Test lock key patterns."""
        lock_key = RedisSchema.Lock.trip_lock("TRP-123")
        info_key = RedisSchema.Lock.lock_info("TRP-123")

        assert lock_key == "lock:trip:TRP-123"
        assert info_key == "lock:info:TRP-123"

    def test_output_keys_consistency(self):
        """Test output key consistency across agents."""
        trip_id = "TRP-999"
        output_keys = {
            agent: RedisSchema.Trip.output(trip_id, agent)
            for agent in ["safety", "scoring", "support"]
        }

        assert output_keys["safety"] == "trip:TRP-999:safety_output"
        assert output_keys["scoring"] == "trip:TRP-999:scoring_output"
        assert output_keys["support"] == "trip:TRP-999:support_output"


# ──────────────────────────────────────────────────────────────────────────────
# Mock tests for cache warming flow
# ──────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
class TestCacheWarmingFlow:
    """Tests for the cache warming workflow."""

    async def test_event_driven_warming_flow(self):
        """Test event-driven warming workflow."""
        # Setup mocks
        redis_client = AsyncMock()
        db = AsyncMock()

        # Mock DB responses
        db.get_event_by_id.return_value = {
            "event_id": "EVT-123",
            "trip_id": "TRP-456",
            "event_type": "harsh_brake",
            "severity": "high",
            "data": {"g_force": -0.75},
        }
        db.get_trip_metadata.return_value = {
            "trip_id": "TRP-456",
            "driver_id": "DRV-789",
            "truck_id": "TRK-001",
            "distance_km": 45.2,
        }

        # Verify cache requirements
        reqs = get_cache_requirements("harsh_brake", "safety")
        assert reqs["ttl"] == 300

        # Simulate warming flow
        event_key = RedisSchema.Trip.agent_data("TRP-456", "safety", "current_event")
        context_key = RedisSchema.Trip.agent_data("TRP-456", "safety", "trip_context")

        event_data = await db.get_event_by_id("EVT-123")
        trip_data = await db.get_trip_metadata("TRP-456")

        # Verify mocks were called
        db.get_event_by_id.assert_called_once_with("EVT-123")
        db.get_trip_metadata.assert_called_once_with("TRP-456")

        # Verify data is in expected format
        assert event_data["event_id"] == "EVT-123"
        assert trip_data["driver_id"] == "DRV-789"

    async def test_aggregation_driven_warming_flow(self):
        """Test aggregation-driven warming workflow."""
        # Setup mocks
        redis_client = AsyncMock()
        db = AsyncMock()

        # Mock DB responses for aggregation-driven
        db.get_all_pings_for_trip.return_value = [
            {
                "event_id": f"EVT-{i:03d}",
                "trip_id": "TRP-456",
                "event_type": "harsh_brake" if i % 3 == 0 else "normal",
                "timestamp": f"2024-01-01T{i:02d}:00:00Z",
                "data": {"g_force": -0.75 if i % 3 == 0 else 0},
            }
            for i in range(12)
        ]
        db.get_trip_metadata.return_value = {
            "trip_id": "TRP-456",
            "driver_id": "DRV-789",
            "distance_km": 150.0,
        }
        db.get_rolling_average_score.return_value = 75.5

        # Verify warming type
        warming_type = get_warming_type("end_of_trip")
        assert warming_type == "aggregation-driven"

        # Fetch data
        all_pings = await db.get_all_pings_for_trip("TRP-456")
        rolling_avg = await db.get_rolling_average_score("DRV-789", n=3)

        # Verify
        db.get_all_pings_for_trip.assert_called_once_with("TRP-456")
        db.get_rolling_average_score.assert_called_once_with("DRV-789", n=3)
        assert len(all_pings) == 12
        assert rolling_avg == 75.5

    async def test_cache_warming_ttl_selection(self):
        """Test that TTL is selected correctly for different warming types."""
        # Event-driven events should have shorter TTL
        event_driven_ttl = get_cache_requirements("harsh_brake", "safety")["ttl"]
        assert event_driven_ttl == 300  # 5 minutes

        # Aggregation-driven should have longer TTL
        agg_driven_ttl = get_cache_requirements("end_of_trip", "scoring")["ttl"]
        assert agg_driven_ttl == 3600  # 1 hour

    async def test_no_double_warming(self):
        """Test that same data isn't warmed multiple times."""
        trip_id = "TRP-123"
        warming_calls = set()

        # Track which data types are warmed
        event_driven = RedisSchema.Trip.event_driven_cache(trip_id, "safety")
        agg_driven = RedisSchema.Trip.aggregation_driven_cache(trip_id, "scoring")

        # Verify no overlapping keys
        event_driven_vals = set(event_driven.values())
        agg_driven_vals = set(agg_driven.values())

        overlap = event_driven_vals & agg_driven_vals
        assert len(overlap) == 0, "Event and aggregation warming should not overlap"


# ──────────────────────────────────────────────────────────────────────────────
# Integration-like tests
# ──────────────────────────────────────────────────────────────────────────────


class TestCacheWarmingIntegration:
    """Integration tests for cache warming."""

    def test_all_event_types_have_warming_strategy(self):
        """Verify all events in EventMatrix have defined warming strategies."""
        from common.config.events import EVENT_MATRIX

        for event_type in EVENT_MATRIX.keys():
            warming_type = get_warming_type(event_type)
            # warming_type can be None for events that don't need warming
            # but it should be explicitly None, not missing
            assert warming_type is not None or get_agents_to_dispatch(event_type) == []

    def test_event_driven_agents_have_correct_cache_keys(self):
        """Test that event-driven agents have the correct cache keys defined."""
        # These events should use event-driven warming
        event_driven_events = ["harsh_brake", "collision", "driver_complaint"]

        for event in event_driven_events:
            agents = get_agents_to_dispatch(event)
            warming_type = get_warming_type(event)
            if agents and warming_type == "event-driven":
                for agent in agents:
                    reqs = get_cache_requirements(event, agent)
                    assert len(reqs["needs"]) > 0

    def test_aggregation_driven_agents_have_expensive_queries(self):
        """Test that aggregation-driven agents explicitly mention expensive queries."""
        # end_of_trip should trigger aggregation-driven warming
        warming_type = get_warming_type("end_of_trip")
        assert warming_type == "aggregation-driven"

        agents = get_agents_to_dispatch("end_of_trip")
        assert "scoring" in agents

        # Scoring should need all_pings
        scoring_reqs = get_cache_requirements("end_of_trip", "scoring")
        assert "all_pings" in scoring_reqs["needs"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
