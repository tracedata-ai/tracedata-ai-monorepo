"""
Shared test fixtures for the TraceData agent pipeline test suite.
All fixtures use mocks / fakeredis — no running Docker or Redis required.
"""

import importlib
import json
import os
import sys
import types
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")


def _ensure_redis_asyncio_stub() -> None:
    try:
        importlib.import_module("redis.asyncio")
        return
    except ModuleNotFoundError:
        pass

    redis_pkg = types.ModuleType("redis")
    asyncio_mod = types.ModuleType("redis.asyncio")

    class _StubPubSub:
        async def subscribe(self, *_args, **_kwargs):
            return None

    class _StubRedis:
        def __getattr__(self, _name):
            return AsyncMock()

        def pubsub(self):
            return _StubPubSub()

    def from_url(*_args, **_kwargs):
        return _StubRedis()

    asyncio_mod.from_url = from_url
    redis_pkg.asyncio = asyncio_mod
    sys.modules["redis"] = redis_pkg
    sys.modules["redis.asyncio"] = asyncio_mod


_ensure_redis_asyncio_stub()


def _ensure_celery_stub() -> None:
    try:
        celery_mod = importlib.import_module("celery")
    except ModuleNotFoundError:
        celery_mod = types.ModuleType("celery")
        sys.modules["celery"] = celery_mod

    if not hasattr(celery_mod, "shared_task"):
        def shared_task(*_args, **_kwargs):
            def _decorator(fn):
                fn.run = fn
                return fn

            return _decorator

        celery_mod.shared_task = shared_task


_ensure_celery_stub()

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
    Fully-mocked RedisClient: ingestion buffers, legacy pop/push, and raw _client.
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
    client.pop = AsyncMock(return_value=None)
    client.push = AsyncMock()
    client.zpop = AsyncMock(return_value=None)
    inner = MagicMock()
    inner.get = AsyncMock(return_value=None)
    inner.incr = AsyncMock(return_value=1)
    inner.set = AsyncMock()
    inner.setex = AsyncMock()
    inner.publish = AsyncMock()
    client._client = inner
    return client


@pytest.fixture
def mock_db_session() -> MagicMock:
    """Mock SQLAlchemy AsyncSession."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_db() -> MagicMock:
    """Mock DBManager for orchestrator tests."""
    db_manager = MagicMock()
    db_manager.acquire_lock = AsyncMock(return_value="orchestrator")
    db_manager.release_lock = AsyncMock()
    db_manager.fail_event = AsyncMock()
    db_manager.get_trip = AsyncMock(return_value=None)
    db_manager.create_trip = AsyncMock(return_value={"trip_id": "test_trip"})
    db_manager.update_trip = AsyncMock()
    return db_manager


@pytest.fixture
def mock_celery() -> MagicMock:
    """Mock Celery app instance."""
    celery_app = MagicMock()
    celery_app.send_task = MagicMock(return_value=MagicMock(id="task-123"))
    return celery_app
