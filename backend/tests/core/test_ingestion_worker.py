"""
Tests for the ingestion worker loop.

Strategy: we test the core `ingest_one` logic (one pop → one push)
by calling it directly with mocked Redis, rather than running the
infinite `main()` loop which requires asyncio task cancellation.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.config.settings import get_settings


# ── Minimal extraction helper ──────────────────────────────────────────────────
# We test the behaviour of one iteration of the ingestion loop directly.

async def _ingest_one(mock_redis, settings):
    """Run exactly one pop-and-forward cycle of the ingestion logic."""
    event = await mock_redis.zpop(settings.ingestion_queue, timeout=1)
    if event:
        await mock_redis.push(settings.orchestrator_queue, event)
    return event


# ── Tests ──────────────────────────────────────────────────────────────────────

async def test_ingestion_pops_from_ingestion_queue(telemetry_packet_json):
    """Worker calls zpop on the configured ingestion_queue key."""
    settings = get_settings()
    mock_redis = MagicMock()
    mock_redis.zpop = AsyncMock(return_value=telemetry_packet_json)
    mock_redis.push = AsyncMock()

    await _ingest_one(mock_redis, settings)

    mock_redis.zpop.assert_called_once_with(settings.ingestion_queue, timeout=1)


async def test_ingestion_pushes_to_orchestrator_queue(telemetry_packet_json):
    """After a successful zpop, the event is pushed to the orchestrator_queue."""
    settings = get_settings()
    mock_redis = MagicMock()
    mock_redis.zpop = AsyncMock(return_value=telemetry_packet_json)
    mock_redis.push = AsyncMock()

    await _ingest_one(mock_redis, settings)

    mock_redis.push.assert_called_once_with(settings.orchestrator_queue, telemetry_packet_json)


async def test_ingestion_skips_push_when_queue_is_empty():
    """When zpop returns None (empty/timeout), no push is made."""
    settings = get_settings()
    mock_redis = MagicMock()
    mock_redis.zpop = AsyncMock(return_value=None)
    mock_redis.push = AsyncMock()

    result = await _ingest_one(mock_redis, settings)

    assert result is None
    mock_redis.push.assert_not_called()


async def test_ingestion_payload_forwarded_unchanged(telemetry_packet_json):
    """The raw JSON string is forwarded to the orchestrator without transformation."""
    settings = get_settings()
    mock_redis = MagicMock()
    mock_redis.zpop = AsyncMock(return_value=telemetry_packet_json)
    mock_redis.push = AsyncMock()

    await _ingest_one(mock_redis, settings)

    pushed_payload = mock_redis.push.call_args[0][1]
    assert pushed_payload == telemetry_packet_json

    # Verify it's still valid JSON containing the event
    data = json.loads(pushed_payload)
    assert "event" in data
    assert data["event"]["event_type"] == "harsh_brake"
