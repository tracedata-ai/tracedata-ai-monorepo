"""
Tests for ``TDAgentBase`` (Celery + IntentCapsule) success path and Redis side-effects.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base.agent import TDAgentBase


class StubAgent(TDAgentBase):
    """Minimal domain agent for unit tests."""

    AGENT_NAME = "stub"

    async def _execute(
        self, trip_id: str, cache_data: dict[str, Any]
    ) -> dict[str, Any]:
        return {"status": "ok", "trip_id": trip_id, "keys": len(cache_data)}

    def _get_repos(self) -> dict[str, Any]:
        return {}


def _capsule_dict() -> dict[str, Any]:
    return {
        "trip_id": "TRIP-UNIT-1",
        "agent": "stub",
        "device_event_id": "DEV-UNIT-1",
        "priority": 3,
        "tool_whitelist": [],
        "step_to_tools": {},
        "ttl_seconds": 600,
        "token": None,
    }


@pytest.mark.asyncio
async def test_td_agent_run_sets_output_and_publishes():
    mock_engine = MagicMock()
    inner = MagicMock()
    inner.get = AsyncMock(return_value=None)
    inner.set = AsyncMock()
    inner.publish = AsyncMock()
    redis_client = MagicMock()
    redis_client._client = inner

    with patch("agents.orchestrator.db_manager.DBManager") as MockDB:
        MockDB.return_value.release_lock = AsyncMock()
        agent = StubAgent(mock_engine, redis_client=redis_client)
        result = await agent.run(_capsule_dict())

    assert result["status"] == "ok"
    inner.set.assert_called_once()
    inner.publish.assert_called_once()
    args = inner.publish.call_args[0]
    payload = json.loads(args[1])
    assert payload["status"] == "success"
    assert payload["agent"] == "stub"


@pytest.mark.asyncio
async def test_td_agent_release_lock_uses_device_event_id_from_capsule():
    mock_engine = MagicMock()
    inner = MagicMock()
    inner.get = AsyncMock(return_value=None)
    inner.set = AsyncMock()
    inner.publish = AsyncMock()
    redis_client = MagicMock()
    redis_client._client = inner

    with patch("agents.orchestrator.db_manager.DBManager") as MockDB:
        inst = MockDB.return_value
        inst.release_lock = AsyncMock()
        agent = StubAgent(mock_engine, redis_client=redis_client)
        await agent.run(_capsule_dict())

    inst.release_lock.assert_awaited_once_with("DEV-UNIT-1")
