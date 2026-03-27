"""
Shared test fixtures for the TraceData agent pipeline test suite.
All fixtures use mocks / fakeredis — no running Docker or Redis required.
"""

import json
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

# ── Fake Telemetry Packet ──────────────────────────────────────────────────────


@pytest.fixture
def trip_id() -> str:
    return "TRIP-TEST-001"


@pytest.fixture
def event_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def telemetry_packet(trip_id, event_id) -> dict:
    """A complete TelemetryPacket-shaped dict matching the real schema."""
    return {
        "ping_type": "high_speed",
        "source": "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id": event_id,
            "device_event_id": "DEV-HB-001",
            "trip_id": trip_id,
            "truck_id": "TRUCK-101",
            "driver_id": "DRIVER-77",
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
            "location": {"lat": 1.2863, "lon": 103.8519},
            "details": {"g_force": -0.85, "speed_kmh": 85},
            "schema_version": "event_v1",
        },
    }


@pytest.fixture
def telemetry_packet_json(telemetry_packet) -> str:
    return json.dumps(telemetry_packet)


# ── Mock Redis Client ──────────────────────────────────────────────────────────


@pytest.fixture
def mock_redis() -> MagicMock:
    """
    A fully-mocked RedisClient with the new pipeline methods.
    """
    client = MagicMock()
    client.pop_from_buffer = AsyncMock(return_value=None)
    client.pop_from_processed = AsyncMock(return_value=None)
    client.push_to_buffer = AsyncMock()
    client.push_to_processed = AsyncMock()
    client.push_to_rejected = AsyncMock()
    client.store_trip_context = AsyncMock()
    client.get_trip_context = AsyncMock(return_value=None)
    client.close = AsyncMock()
    return client


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock SQLAlchemy AsyncSession."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session
