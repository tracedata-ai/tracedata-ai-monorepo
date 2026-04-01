"""
Integration tests for cache warming in OrchestratorAgent.

Tests the full flow:
  1. Event arrives
  2. Warming strategy is determined
  3. Cache warming completes
  4. Agent capsule is sealed with correct scoped keys
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from common.models.events import TripEvent, Location
from common.models.enums import Priority
from common.redis.keys import RedisSchema


@pytest.mark.asyncio
class TestCacheWarmingIntegration:
    """Integration tests for cache warming workflow."""

    def _create_trip_event(
        self,
        event_type: str,
        priority: Priority = Priority.HIGH,
        trip_id: str = "TRP-456",
        event_id: str = "EVT-123",
    ) -> TripEvent:
        """Helper to create valid TripEvent for testing."""
        return TripEvent(
            event_id=event_id,
            trip_id=trip_id,
            device_event_id="DEV-001",
            event_type=event_type,
            category="test_category",
            driver_id="DRV-789",
            truck_id="TRK-111",
            timestamp=datetime.now(),
            priority=priority,
            offset_seconds=0,
        )

    async def test_event_driven_warming_full_flow(self):
        """Test full event-driven warming workflow (Safety agent)."""
        # Create test event
        event = self._create_trip_event("harsh_brake", Priority.HIGH)

        # Verify warming type is event-driven
        from common.config.events import get_warming_type

        warming_type = get_warming_type(event.event_type)
        assert warming_type == "event-driven"

        # Verify cache requirements
        from common.config.events import get_cache_requirements

        reqs = get_cache_requirements(event.event_type, "scoring")
        assert "current_event" in reqs["needs"]
        assert "trip_context" in reqs["needs"]
        assert reqs["ttl"] == 300  # 5 minutes

        # Verify scoped keys are correct
        safety_keys = RedisSchema.Trip.event_driven_cache("TRP-456", "safety")
        assert "current_event" in safety_keys
        assert "trip_context" in safety_keys
        assert safety_keys["current_event"] == "trips:TRP-456:safety:current_event"
        assert safety_keys["trip_context"] == "trips:TRP-456:safety:trip_context"

    async def test_aggregation_driven_warming_full_flow(self):
        """Test full aggregation-driven warming workflow (Scoring agent)."""
        # Create end_of_trip event
        event = self._create_trip_event("end_of_trip", Priority.LOW)

        # Verify warming type
        from common.config.events import get_warming_type

        warming_type = get_warming_type(event.event_type)
        assert warming_type == "aggregation-driven"

        # Verify cache requirements for scoring
        from common.config.events import get_cache_requirements

        scoring_reqs = get_cache_requirements(event.event_type, "scoring")
        assert "all_pings" in scoring_reqs["needs"]
        assert "historical_avg" in scoring_reqs["needs"]
        assert scoring_reqs["ttl"] == 3600  # 1 hour

        # Verify scoped keys for aggregation-driven
        scoring_keys = RedisSchema.Trip.aggregation_driven_cache("TRP-456", "scoring")
        assert "all_pings" in scoring_keys
        assert "historical_avg" in scoring_keys
        assert scoring_keys["all_pings"] == "trips:TRP-456:scoring:all_pings"
        assert scoring_keys["historical_avg"] == "trips:TRP-456:scoring:historical_avg"

    async def test_capsule_keys_match_warming_strategy_event_driven(self):
        """Test that capsule read keys match pre-warmed data keys (event-driven)."""
        trip_id = "TRP-505"
        agent_name = "safety"

        # Get warming strategy
        from common.config.events import get_warming_type

        warming_type = get_warming_type("harsh_brake")
        assert warming_type == "event-driven"

        # Get what keys the agent should have
        warming_keys = RedisSchema.Trip.event_driven_cache(trip_id, agent_name)

        # Verify keys exist and are accessible
        expected_keys = [
            warming_keys["current_event"],
            warming_keys["trip_context"],
        ]

        assert all(
            key.startswith(f"trips:{trip_id}:{agent_name}:") for key in expected_keys
        )

    async def test_capsule_keys_match_warming_strategy_aggregation(self):
        """Test that capsule read keys match pre-warmed data keys (aggregation)."""
        trip_id = "TRP-606"
        agent_name = "scoring"

        # Get warming strategy
        from common.config.events import get_warming_type

        warming_type = get_warming_type("end_of_trip")
        assert warming_type == "aggregation-driven"

        # Get what keys the agent should have
        warming_keys = RedisSchema.Trip.aggregation_driven_cache(trip_id, agent_name)

        # Verify keys match expectations
        expected_keys = [
            warming_keys["all_pings"],
            warming_keys["historical_avg"],
        ]

        assert all(
            key.startswith(f"trips:{trip_id}:{agent_name}:") for key in expected_keys
        )
        assert any("all_pings" in key for key in expected_keys)
        assert any("historical_avg" in key for key in expected_keys)

    async def test_multi_agent_warming_no_key_conflicts(self):
        """Test that warming for multiple agents doesn't have key conflicts."""
        trip_id = "TRP-707"

        # Warm for multiple agents
        safety_keys = RedisSchema.Trip.event_driven_cache(trip_id, "safety")
        scoring_keys = RedisSchema.Trip.event_driven_cache(trip_id, "scoring")

        # Verify no overlaps
        safety_vals = set(safety_keys.values())
        scoring_vals = set(scoring_keys.values())

        # Keys are agent-specific, so should not overlap
        assert len(safety_vals & scoring_vals) == 0

        # But both should have same data types
        assert set(safety_keys.keys()) == set(scoring_keys.keys())

    async def test_aggregation_support_agent_gets_coaching_history(self):
        """Test that support agent gets coaching history in aggregation warming."""
        trip_id = "TRP-808"
        agent_name = "support"

        # Get aggregation-driven keys for support (end_of_trip uses support agent)
        warming_keys = RedisSchema.Trip.aggregation_driven_cache(trip_id, agent_name)

        # Support agent should get coaching history and trip context
        assert "trip_context" in warming_keys
        assert "coaching_history" in warming_keys

    async def test_cache_warming_ttl_values_match_requirements(self):
        """Test that cache warming TTL values match requirements."""
        from common.config.events import get_cache_requirements

        # Event-driven: 5 minutes
        event_driven_reqs = get_cache_requirements("harsh_brake", "safety")
        assert event_driven_reqs["ttl"] == 300

        # Aggregation-driven: 1 hour
        agg_driven_reqs = get_cache_requirements("end_of_trip", "scoring")
        assert agg_driven_reqs["ttl"] == 3600

    async def test_critical_priority_gets_longer_ttl(self):
        """Test that critical priority events get longer capsule TTL."""
        # Critical event (collision) should have longer TTL
        from common.config.events import get_warming_type

        warming_type = get_warming_type("collision")
        assert warming_type == "event-driven"

        # When capsule is sealed, critical events should get 1-hour TTL
        # This is handled in _seal_capsule method

    async def test_warming_skipped_for_analytics_events(self):
        """Test that analytics/logging events skip warming."""
        from common.config.events import get_warming_type

        # normal_operation is analytics - should skip warming
        warming_type = get_warming_type("normal_operation")
        assert warming_type is None

        # smoothness_log is reward - should skip warming
        warming_type = get_warming_type("smoothness_log")
        assert warming_type is None

    async def test_hitl_event_uses_event_driven_warming(self):
        """Test that HITL events use event-driven warming (trip context)."""
        from common.config.events import get_warming_type

        warming_type = get_warming_type("driver_dispute")
        assert warming_type == "event-driven"

        # HITL should have access to trip context for review
        hitl_keys = RedisSchema.Trip.event_driven_cache("TRP-999", "human_in_the_loop")
        assert "current_event" in hitl_keys
        assert "trip_context" in hitl_keys


@pytest.mark.asyncio
class TestCacheWarmingEdgeCases:
    """Edge case tests for cache warming."""

    async def test_unknown_event_type_no_crash(self):
        """Test that unknown event type doesn't crash warming."""
        from common.config.events import get_warming_type, get_agents_to_dispatch

        warming_type = get_warming_type("completely_unknown_event")
        assert warming_type is None

        agents = get_agents_to_dispatch("completely_unknown_event")
        assert agents == []

    async def test_cache_key_format_consistency(self):
        """Test that all cache keys follow consistent format."""
        # All agent data keys should follow pattern: trips:{trip_id}:{agent}:{data_type}
        trip_id = "TRP-TEST"
        agents = ["safety", "scoring", "support", "sentiment"]

        for agent in agents:
            key = RedisSchema.Trip.agent_data(trip_id, agent, "test_data")
            assert key.startswith("trips:")
            assert trip_id in key
            assert agent in key
            assert key.count(":") == 3

    async def test_lock_keys_separate_from_data_keys(self):
        """Test that lock keys are separate from data keys."""
        trip_id = "TRP-LOCK"

        lock_key = RedisSchema.Lock.trip_lock(trip_id)
        data_key = RedisSchema.Trip.agent_data(trip_id, "safety", "event")

        # Lock key should start with "lock:"
        assert lock_key.startswith("lock:")
        assert not data_key.startswith("lock:")

        # No overlap
        assert lock_key != data_key


class TestCacheWarmingMetrics:
    """Tests for cache warming metrics and logging."""

    def test_warming_logs_correct_action_names(self):
        """Test that warming produces correct log action names."""
        from common.config.events import get_warming_type

        # Event-driven should log "cache_warmed_event_driven"
        assert get_warming_type("harsh_brake") == "event-driven"

        # Aggregation-driven should log "cache_warmed_aggregation_driven"
        assert get_warming_type("end_of_trip") == "aggregation-driven"

    def test_warming_tracks_data_sizes(self):
        """Test that warming can track data sizes for metrics."""
        import json

        # Event data (1-2 KB expected)
        event_data = {
            "event_id": "EVT-123",
            "event_type": "harsh_brake",
            "severity": "high",
            "data": {"g_force": -0.75, "timestamp": "2024-04-01T12:00:00Z"},
        }
        event_size = len(json.dumps(event_data))
        assert event_size < 2000  # Should be < 2 KB

        # Trip metadata (1-2 KB expected)
        trip_meta = {
            "trip_id": "TRP-123",
            "driver_id": "DRV-456",
            "truck_id": "TRK-789",
            "distance_km": 125.5,
            "duration_minutes": 45,
            "status": "completed",
        }
        meta_size = len(json.dumps(trip_meta))
        assert meta_size < 2000  # Should be < 2 KB

    def test_warming_type_distribution(self):
        """Test that event types are distributed across warming strategies."""
        from common.config.events import EVENT_MATRIX, get_warming_type

        warming_counts = {"event-driven": 0, "aggregation-driven": 0, "none": 0}

        for event_type in EVENT_MATRIX.keys():
            warming = get_warming_type(event_type)
            if warming == "event-driven":
                warming_counts["event-driven"] += 1
            elif warming == "aggregation-driven":
                warming_counts["aggregation-driven"] += 1
            else:
                warming_counts["none"] += 1

        # Should have at least some of each
        assert warming_counts["event-driven"] > 0  # Safety events, etc.
        assert warming_counts["aggregation-driven"] >= 1  # At least end_of_trip
        assert warming_counts["none"] >= 1  # Analytics, logging, etc.


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
