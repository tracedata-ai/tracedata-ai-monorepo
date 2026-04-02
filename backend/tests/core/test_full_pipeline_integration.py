"""
Integration-style tests for the ingestion sidecar (mocked DB + Redis).

These exercise ``IngestionSidecar.process`` end-to-end with AsyncMock DB and
a shared Redis mock — no Docker stack required. For live stack checks, use
manual or CI jobs against docker compose.
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from common.models.events import TripEvent
from core.ingestion.sidecar import IngestionSidecar

pytestmark = pytest.mark.integration


@pytest.fixture
def telemetry_packet():
    return {
        "ping_type": "high_speed",
        "source": "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id": "evt-e2e-001",
            "device_event_id": "dev-e2e-001",
            "trip_id": "trip-e2e-001",
            "truck_id": "truck-e2e-001",
            "driver_id": "driver-e2e-001",
            "event_type": "collision",
            "category": "safety",
            "priority": "critical",
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
            "location": {"lat": 1.2863, "lon": 103.8519},
            "details": {"impact_force": 2.5, "direction": "rear"},
            "schema_version": "event_v1",
        },
    }


class TestFullPipelineFlow:
    @pytest.mark.asyncio
    async def test_sidecar_validates_and_routes_to_processed(self, mock_redis):
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False
        mock_db.insert_event = AsyncMock()
        mock_redis.push_to_processed = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)
        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-pipeline-001",
                "device_event_id": "dev-pipeline-001",
                "trip_id": "trip-001",
                "truck_id": "truck-001",
                "driver_id": "driver-001",
                "event_type": "collision",
                "category": "safety",
                "priority": "critical",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 120,
                "trip_meter_km": 5.4,
                "odometer_km": 124565.4,
                "location": {"lat": 1.29, "lon": 103.85},
                "details": {"impact": "rear"},
                "schema_version": "event_v1",
            },
        }

        result = await sidecar.process(packet, truck_id="truck-001")
        assert result.ok is True
        assert isinstance(result.trip_event, TripEvent)
        mock_db.insert_event.assert_called_once()
        mock_redis.push_to_processed.assert_called_once()
        args = mock_redis.push_to_processed.call_args[0]
        assert args[2] == 0

    @pytest.mark.asyncio
    async def test_sidecar_rejects_duplicates(self, mock_redis):
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = True
        mock_redis.push_to_rejected = AsyncMock()

        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)
        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-dup-001",
                "device_event_id": "dev-dup-001",
                "trip_id": "trip-dup",
                "truck_id": "truck-dup",
                "driver_id": "driver-dup",
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

        result = await sidecar.process(packet, truck_id="truck-dup")
        assert result.ok is False
        assert result.reason == "duplicate"
        mock_redis.push_to_rejected.assert_called_once()

    @pytest.mark.asyncio
    async def test_sidecar_validates_schema(self, mock_redis):
        mock_db = AsyncMock()
        mock_redis.push_to_rejected = AsyncMock()
        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-invalid-001",
                "device_event_id": "dev-invalid-001",
                "trip_id": "trip-invalid",
                "truck_id": "truck-invalid",
                "driver_id": "driver-invalid",
                "category": "safety",
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

        result = await sidecar.process(packet, truck_id="truck-invalid")
        assert result.ok is False
        assert result.reason == "schema_invalid"
        mock_redis.push_to_rejected.assert_called_once()

    @pytest.mark.asyncio
    async def test_gps_coordinates_rounded_to_2_decimals(self, mock_redis):
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False
        mock_redis.push_to_processed = AsyncMock()
        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-gps-001",
                "device_event_id": "dev-gps-001",
                "trip_id": "trip-gps",
                "truck_id": "truck-gps",
                "driver_id": "driver-gps",
                "event_type": "harsh_brake",
                "category": "test",
                "priority": "high",
                "timestamp": datetime.now(UTC).isoformat(),
                "offset_seconds": 100,
                "trip_meter_km": 10.0,
                "odometer_km": 100000.0,
                "location": {"lat": 1.286321456, "lon": 103.851923789},
                "details": {},
                "schema_version": "event_v1",
            },
        }

        await sidecar.process(packet, truck_id="truck-gps")
        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**json.loads(args[1]))
        assert routed_event.location.lat == 1.29
        assert routed_event.location.lon == 103.85

    @pytest.mark.asyncio
    async def test_driver_id_anonymized_if_required(self, mock_redis):
        mock_db = AsyncMock()
        mock_db.event_exists.return_value = False
        mock_redis.push_to_processed = AsyncMock()
        sidecar = IngestionSidecar(db=mock_db, redis=mock_redis)

        packet = {
            "ping_type": "high_speed",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": "evt-anon-001",
                "device_event_id": "dev-anon-001",
                "trip_id": "trip-anon",
                "truck_id": "truck-anon",
                "driver_id": "DRIVER-12345",
                "event_type": "harsh_brake",
                "category": "test",
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

        await sidecar.process(packet, truck_id="truck-anon")
        args = mock_redis.push_to_processed.call_args[0]
        routed_event = TripEvent(**json.loads(args[1]))
        assert routed_event.driver_id.startswith("DRV-ANON-")
