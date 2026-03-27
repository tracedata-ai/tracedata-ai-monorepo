import json
from unittest.mock import AsyncMock, patch

import pytest

from common.models.events import TripEvent
from core.ingestion.sidecar import IngestionSidecar


@pytest.fixture
def sidecar(mock_redis):
    return IngestionSidecar(mock_redis)


@pytest.mark.asyncio
async def test_pipeline_success_harsh_brake(sidecar, telemetry_packet, mock_db_session):
    """
    Test 7-step success for a harsh_brake event.
    Verifies:
      1. Schema valid
      2. Matrix override (priority/category)
      3. No injection
      4. PII Scrubbed
      5. DB Write OK
      6. Routed to processed
    """
    # Force event_type to harsh_brake to match MATRIX test
    telemetry_packet["event"]["event_type"] = "harsh_brake"
    # Set different priority to test override
    telemetry_packet["event"]["priority"] = "low"

    # Mock DB: event does not exist (idempotency passed)
    mock_db_session.execute.return_value = MagicMock(scalar_one_or_none=lambda: None)

    with patch(
        "core.ingestion.sidecar.AsyncSessionLocal",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_db_session)),
    ):
        success = await sidecar.process_packet(telemetry_packet)

    assert success is True

    # Check 7. ROUTE: Success (zpush to processed)
    # Harsh brake in MATRIX is Priority.HIGH (score 3)
    sidecar.redis.push_to_processed.assert_called_once()
    args = sidecar.redis.push_to_processed.call_args[0]
    # args: (key, payload, score)
    assert args[2] == 3  # High Priority Override

    # Check 4. PII Scrubbed
    pushed_event = TripEvent(**json.loads(args[1]))
    assert pushed_event.driver_id.startswith("DRV-ANON-")
    assert pushed_event.priority == "high"
    
    # Check GPS rounding (2dp)
    # Original: 1.2863, 103.8519 -> 1.29, 103.85
    assert pushed_event.location.lat == 1.29
    assert pushed_event.location.lon == 103.85


@pytest.mark.asyncio
async def test_pipeline_rejected_injection(sidecar, telemetry_packet):
    """
    Step 3: Test rejection due to SQL injection.
    """
    telemetry_packet["event"]["details"]["note"] = "SELECT * FROM drivers;"

    success = await sidecar.process_packet(telemetry_packet)

    assert success is False
    # Check 7b. ROUTE: Failure (zpush to rejected)
    sidecar.redis.push_to_rejected.assert_called_once()
    args = sidecar.redis.push_to_rejected.call_args[0]
    assert "injection_detected" in args[1]


@pytest.mark.asyncio
async def test_pipeline_rejected_invalid_schema(sidecar, telemetry_packet):
    """
    Step 1: Test rejection due to missing required field.
    """
    del telemetry_packet["event"]["event_type"]

    success = await sidecar.process_packet(telemetry_packet)

    assert success is False
    sidecar.redis.push_to_rejected.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_idempotency_skip(sidecar, telemetry_packet, mock_db_session):
    """
    Step 5: Test idempotency skip.
    If event already exists, it should return success but NOT push to processed again.
    """
    # Mock DB: event exists (idempotency failed)
    mock_db_session.execute.return_value = MagicMock(
        scalar_one_or_none=lambda: MagicMock()
    )

    with patch(
        "core.ingestion.sidecar.AsyncSessionLocal",
        return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_db_session)),
    ):
        success = await sidecar.process_packet(telemetry_packet)

    assert success is True
    # Should NOT have pushed to processed or rejected
    sidecar.redis.push_to_processed.assert_not_called()
    sidecar.redis.push_to_rejected.assert_not_called()


from unittest.mock import MagicMock
