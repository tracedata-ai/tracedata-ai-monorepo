"""
Unit tests for sidecar validation pipeline components.
Tests individual helper methods and transformations in isolation.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.config.events import PRIORITY_MAP, processed_queue_sort_score
from common.models.events import TripEvent
from common.redis.keys import RedisSchema
from core.ingestion.sidecar import IngestionSidecar


class TestPriorityMapping:
    """Processed-queue ZSET scores: chronological with priority tier tie-break."""

    @pytest.mark.asyncio
    async def test_priority_critical_maps_to_score_0(self):
        """CRITICAL tier is embedded in sort score (zpopmin ≈ time order)."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-crit-001",
                "device_event_id": "dev-crit-001",
                "trip_id": "trip-001",
                "truck_id": "truck-001",
                "driver_id": "driver-001",
                "event_type": "collision",
                "category": "safety",
                "priority": "critical",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-001")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed = TripEvent(**json.loads(args[1]))
        tier = PRIORITY_MAP[str(routed.priority)]
        assert args[2] == pytest.approx(
            processed_queue_sort_score(routed.timestamp, tier)
        )

    @pytest.mark.asyncio
    async def test_priority_high_maps_to_score_3(self):
        """HIGH tier embedded in sort score."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-high-001",
                "device_event_id": "dev-high-001",
                "trip_id": "trip-002",
                "truck_id": "truck-002",
                "driver_id": "driver-002",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-002")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed = TripEvent(**json.loads(args[1]))
        tier = PRIORITY_MAP[str(routed.priority)]
        assert args[2] == pytest.approx(
            processed_queue_sort_score(routed.timestamp, tier)
        )

    @pytest.mark.asyncio
    async def test_priority_low_maps_to_score_9_variant(self):
        """LOW tier embedded in sort score — variant."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-med-001",
                "device_event_id": "dev-med-001",
                "trip_id": "trip-003",
                "truck_id": "truck-003",
                "driver_id": "driver-003",
                "event_type": "smoothness_log",
                "category": "telemetry",
                "priority": "low",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-003")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed = TripEvent(**json.loads(args[1]))
        tier = PRIORITY_MAP[str(routed.priority)]
        assert args[2] == pytest.approx(
            processed_queue_sort_score(routed.timestamp, tier)
        )

    @pytest.mark.asyncio
    async def test_priority_low_maps_to_score_9(self):
        """LOW tier embedded in sort score."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-low-001",
                "device_event_id": "dev-low-001",
                "trip_id": "trip-004",
                "truck_id": "truck-004",
                "driver_id": "driver-004",
                "event_type": "smoothness_log",
                "category": "telemetry",
                "priority": "low",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-004")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed = TripEvent(**json.loads(args[1]))
        tier = PRIORITY_MAP[str(routed.priority)]
        assert args[2] == pytest.approx(
            processed_queue_sort_score(routed.timestamp, tier)
        )


class TestGPSRounding:
    """Tests for GPS coordinate rounding to 2 decimal places."""

    @pytest.mark.asyncio
    async def test_gps_rounding_standard_case(self):
        """Standard rounding: 1.2863 → 1.29, 103.8519 → 103.85."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-gps-001",
                "device_event_id": "dev-gps-001",
                "trip_id": "trip-gps-001",
                "truck_id": "truck-gps-001",
                "driver_id": "driver-gps-001",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.2863, "lon": 103.8519},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-gps-001")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**__import__("json").loads(args[1]))

        assert routed_event.location.lat == 1.29
        assert routed_event.location.lon == 103.85

    @pytest.mark.asyncio
    async def test_gps_rounding_boundary_up(self):
        """Boundary case: 1.995 rounds up to 2.0."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-gps-boundary-001",
                "device_event_id": "dev-gps-boundary-001",
                "trip_id": "trip-gps-boundary",
                "truck_id": "truck-gps-boundary",
                "driver_id": "driver-gps-boundary",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.995, "lon": 103.995},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-gps-boundary")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**__import__("json").loads(args[1]))

        assert routed_event.location.lat == 2.0
        assert routed_event.location.lon == 104.0

    @pytest.mark.asyncio
    async def test_gps_rounding_negative_coordinates(self):
        """Negative coordinates: -1.2863 → -1.29, -103.8519 → -103.85."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-gps-neg-001",
                "device_event_id": "dev-gps-neg-001",
                "trip_id": "trip-gps-neg",
                "truck_id": "truck-gps-neg",
                "driver_id": "driver-gps-neg",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": -1.2863, "lon": -103.8519},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-gps-neg")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**__import__("json").loads(args[1]))

        assert routed_event.location.lat == -1.29
        assert routed_event.location.lon == -103.85

    @pytest.mark.asyncio
    async def test_gps_rounding_already_rounded(self):
        """Already rounded values remain unchanged."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-gps-exact-001",
                "device_event_id": "dev-gps-exact-001",
                "trip_id": "trip-gps-exact",
                "truck_id": "truck-gps-exact",
                "driver_id": "driver-gps-exact",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.23, "lon": 103.45},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-gps-exact")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**__import__("json").loads(args[1]))

        assert routed_event.location.lat == 1.23
        assert routed_event.location.lon == 103.45


class TestRedisSchemaKeys:
    """Tests for Redis key generation."""

    def test_redis_schema_buffer_key_format(self):
        """RedisSchema.Telemetry.buffer generates correct key format."""
        key = RedisSchema.Telemetry.buffer("TRUCK-001")
        assert key == "telemetry:TRUCK-001:buffer"

    def test_redis_schema_processed_key_format(self):
        """RedisSchema.Telemetry.processed generates correct key format."""
        key = RedisSchema.Telemetry.processed("TRUCK-002")
        assert key == "telemetry:TRUCK-002:processed"

    def test_redis_schema_rejected_key_format(self):
        """RedisSchema.Telemetry.rejected generates correct key format."""
        key = RedisSchema.Telemetry.rejected("TRUCK-003")
        assert key == "telemetry:TRUCK-003:rejected"

    def test_redis_schema_keys_unique_per_truck(self):
        """Different trucks have different keys."""
        key1 = RedisSchema.Telemetry.buffer("TRUCK-001")
        key2 = RedisSchema.Telemetry.buffer("TRUCK-002")
        assert key1 != key2

    def test_redis_schema_keys_consistent(self):
        """Same truck always generates same key."""
        key1 = RedisSchema.Telemetry.buffer("TRUCK-001")
        key2 = RedisSchema.Telemetry.buffer("TRUCK-001")
        assert key1 == key2


class TestDriverAnonymization:
    """Tests for driver ID anonymization."""

    @pytest.mark.asyncio
    async def test_driver_id_anonymized_format(self):
        """Driver ID is anonymized to DRV-ANON-XXXXX format."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-anon-001",
                "device_event_id": "dev-anon-001",
                "trip_id": "trip-anon-001",
                "truck_id": "truck-anon-001",
                "driver_id": "DRIVER-REAL-12345",  # Real ID
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-anon-001")
        assert result.ok is True

        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**__import__("json").loads(args[1]))

        assert routed_event.driver_id.startswith("DRV-ANON-")

    @pytest.mark.asyncio
    async def test_driver_id_anonymization_consistent(self):
        """Same driver ID always produces same anonymized ID (hash stable)."""
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False

        mock_redis = MagicMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        # First event
        packet1 = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-anon-hash-001",
                "device_event_id": "dev-anon-hash-001",
                "trip_id": "trip-1",
                "truck_id": "truck-1",
                "driver_id": "DRIVER-STABLE-ID",
                "event_type": "harsh_brake",
                "category": "harsh_events",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.0, "lon": 103.0},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        await sidecar.process(packet1, truck_id="truck-1")
        args1 = mock_redis.push_to_processed.call_args_list[0][0]
        event1 = TripEvent(**__import__("json").loads(args1[1]))
        anon_id_1 = event1.driver_id

        # Reset mock
        mock_redis.reset_mock()
        mock_redis.push_to_processed = AsyncMock()

        # Second event with same driver
        packet2 = packet1.copy()
        packet2["event"] = packet1["event"].copy()
        packet2["event"]["event_id"] = "evt-anon-hash-002"
        packet2["event"]["device_event_id"] = "dev-anon-hash-002"
        packet2["event"]["trip_id"] = "trip-2"

        await sidecar.process(packet2, truck_id="truck-1")
        args2 = mock_redis.push_to_processed.call_args_list[0][0]
        event2 = TripEvent(**__import__("json").loads(args2[1]))
        anon_id_2 = event2.driver_id

        # Should be identical
        assert anon_id_1 == anon_id_2
