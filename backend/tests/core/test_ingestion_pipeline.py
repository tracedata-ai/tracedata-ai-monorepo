import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from common.models.events import TripEvent
from core.ingestion.sidecar import IngestionSidecar


@pytest.fixture
def mock_db():
    db = AsyncMock()
    db.event_exists.return_value = False
    db.insert_event = AsyncMock()
    return db


@pytest.fixture
def mock_redis():
    redis = MagicMock()
    redis.push_to_processed = AsyncMock()
    redis.push_to_rejected = AsyncMock()
    return redis


@pytest.fixture
def sidecar(mock_db, mock_redis):
    return IngestionSidecar(db=mock_db, redis=mock_redis)


@pytest.mark.asyncio
async def test_pipeline_success_harsh_brake(sidecar, telemetry_packet):
    """
    Test 7-step success for a harsh_brake event.
    """
    telemetry_packet["event"]["event_type"] = "harsh_brake"
    telemetry_packet["event"]["priority"] = "low"

    result = await sidecar.process(telemetry_packet, truck_id="TRK123")

    assert result.ok is True
    assert isinstance(result.trip_event, TripEvent)

    # Check 7. ROUTE: Success (zpush to processed)
    sidecar._redis.push_to_processed.assert_called_once()
    args = sidecar._redis.push_to_processed.call_args[0]

    # Priority for harsh brake should be 3 (HIGH)
    assert args[2] == 3

    pushed_event = TripEvent(**json.loads(args[1]))
    assert pushed_event.driver_id.startswith("DRV-ANON-")

    # Check GPS rounding (2dp)
    assert pushed_event.location.lat == 1.29
    assert pushed_event.location.lon == 103.85


@pytest.mark.asyncio
async def test_pipeline_rejected_injection(sidecar, telemetry_packet):
    """
    Step 3: Test rejection due to SQL injection.
    """
    telemetry_packet["event"]["details"] = {"note": "1'; DROP TABLE drivers;--"}

    result = await sidecar.process(telemetry_packet, truck_id="TRK123")

    assert result.ok is False
    assert result.rejected is True
    sidecar._redis.push_to_rejected.assert_called_once()
    assert "injection:sql_" in result.reason or "injection" in result.reason


@pytest.mark.asyncio
async def test_pipeline_rejected_invalid_schema(sidecar, telemetry_packet):
    """
    Step 1: Test rejection due to missing required field.
    """
    del telemetry_packet["event"]["event_type"]

    result = await sidecar.process(telemetry_packet, truck_id="TRK123")

    assert result.ok is False
    assert result.reason == "schema_invalid"
    sidecar._redis.push_to_rejected.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_idempotency_skip(sidecar, telemetry_packet, mock_db):
    """
    Step 5: Test idempotency skip.
    """
    mock_db.event_exists.return_value = True

    result = await sidecar.process(telemetry_packet, truck_id="TRK123")

    assert result.ok is False
    assert result.reason == "duplicate"

    # It routes duplicates to DLQ per new design
    sidecar._redis.push_to_rejected.assert_called_once()
    sidecar._redis.push_to_processed.assert_not_called()


@pytest.mark.asyncio
async def test_priority_in_processed_event_is_string_not_int(sidecar, telemetry_packet):
    """
    Regression guard: the TripEvent pushed to the processed queue must have
    priority as a Priority StrEnum string ('high'), never as an int (3).

    Before the transformer fix, PRIORITY_MAP[event.priority.value] returned
    an integer score (0/3/6/9) which Pydantic rejected at TripEvent creation.
    """
    result = await sidecar.process(telemetry_packet, truck_id="TRK123")

    assert result.ok is True

    args = sidecar._redis.push_to_processed.call_args[0]
    pushed_event = TripEvent(**json.loads(args[1]))

    # Priority must be the string enum value, not a Redis score integer
    assert isinstance(
        pushed_event.priority, str
    ), f"priority must be a string, got {type(pushed_event.priority)}"
    assert pushed_event.priority in (
        "critical",
        "high",
        "medium",
        "low",
    ), f"priority must be a valid Priority value, got '{pushed_event.priority}'"
    assert pushed_event.priority != 3, "priority must not be the Redis score int"
