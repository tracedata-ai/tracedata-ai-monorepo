"""
Unit tests: orchestrator cache warming (mocked Redis/DB) and Celery task async wiring.
"""

import asyncio
import importlib
import sys
import types
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from common.models.enums import Priority
from common.models.events import TripEvent
from common.redis.keys import RedisSchema


def _preload_orchestrator_agent():
    """Register agents.orchestrator.* so patch() can resolve targets."""
    importlib.import_module("agents.orchestrator.db_manager")
    return importlib.import_module("agents.orchestrator.agent")


def _ensure_minimal_celery_module():
    """Allow tasks/*.py and agents.orchestrator to import if celery is missing."""
    if "celery" in sys.modules:
        return
    try:
        importlib.import_module("celery")
        return
    except ModuleNotFoundError:
        pass

    mod = types.ModuleType("celery")

    class _Conf:
        def update(self, **_k):
            pass

    class Celery:
        def __init__(self, *_, **__):
            self.conf = _Conf()

        def task(self, *_, **__):
            def _decorator(fn):
                return fn

            return _decorator

        def autodiscover_tasks(self, *_, **__):
            pass

    mod.Celery = Celery
    sys.modules["celery"] = mod


def _ensure_langchain_chat_stubs():
    """Stub LLM providers when not installed (orchestrator.agent imports them)."""
    if "langchain_anthropic" not in sys.modules:
        try:
            importlib.import_module("langchain_anthropic")
        except ModuleNotFoundError:
            m = types.ModuleType("langchain_anthropic")
            m.ChatAnthropic = MagicMock
            sys.modules["langchain_anthropic"] = m
    if "langchain_openai" not in sys.modules:
        try:
            importlib.import_module("langchain_openai")
        except ModuleNotFoundError:
            m = types.ModuleType("langchain_openai")
            m.ChatOpenAI = MagicMock
            sys.modules["langchain_openai"] = m


_ensure_minimal_celery_module()
_ensure_langchain_chat_stubs()


def _trip_event(
    event_type: str,
    trip_id: str = "TRP-456",
    event_id: str = "EVT-123",
    device_event_id: str = "DEV-LOCK-1",
) -> TripEvent:
    return TripEvent(
        event_id=event_id,
        trip_id=trip_id,
        device_event_id=device_event_id,
        event_type=event_type,
        category="test_category",
        driver_id="DRV-789",
        truck_id="TRK-111",
        timestamp=datetime.now(),
        priority=Priority.HIGH,
        offset_seconds=0,
    )


@pytest.fixture
def orchestrator_mocks():
    """OrchestratorAgent with LLM and Redis client mocked."""
    orch_mod = _preload_orchestrator_agent()
    fake_redis = MagicMock()
    fake_redis._client = MagicMock()
    fake_redis._client.setex = AsyncMock(return_value=True)

    with (
        patch.object(orch_mod, "_get_llm", return_value=MagicMock()),
        patch.object(orch_mod, "RedisClient", return_value=fake_redis),
    ):
        orch = orch_mod.OrchestratorAgent(truck_ids=[])
    return orch, fake_redis


@pytest.mark.asyncio
async def test_warm_event_driven_writes_scoped_keys(orchestrator_mocks):
    orch, fake_redis = orchestrator_mocks
    event = _trip_event("harsh_brake", trip_id="TRP-WARM-1")

    orch._get_event_data = AsyncMock(
        return_value={
            "event_id": event.event_id,
            "event_type": "harsh_brake",
            "severity": "high",
        }
    )
    orch._get_trip_metadata = AsyncMock(
        return_value={
            "trip_id": event.trip_id,
            "driver_id": "DRV-1",
        }
    )

    await orch._warm_event_driven(event, ["safety"])

    assert fake_redis._client.setex.await_count >= 2
    safety_ev = RedisSchema.Trip.agent_data(event.trip_id, "safety", "current_event")
    safety_ctx = RedisSchema.Trip.agent_data(event.trip_id, "safety", "trip_context")
    keys_called = {c.args[0] for c in fake_redis._client.setex.await_args_list}
    assert safety_ev in keys_called
    assert safety_ctx in keys_called


@pytest.mark.asyncio
async def test_warm_aggregation_driven_scoring_and_support(orchestrator_mocks):
    orch, fake_redis = orchestrator_mocks
    event = _trip_event("end_of_trip", trip_id="TRP-AGG-1")

    orch._get_all_pings_for_trip = AsyncMock(
        return_value=[{"event_type": "ping", "trip_id": event.trip_id}]
    )
    orch._get_trip_metadata = AsyncMock(
        return_value={
            "trip_id": event.trip_id,
            "driver_id": "DRV-2",
        }
    )
    orch._get_rolling_average_score = AsyncMock(return_value=72.5)
    orch._get_coaching_history = AsyncMock(return_value=[{"note": "prior"}])

    await orch._warm_aggregation_driven(event, ["scoring", "support"])

    keys_called = {c.args[0] for c in fake_redis._client.setex.await_args_list}
    assert (
        RedisSchema.Trip.agent_data(event.trip_id, "scoring", "all_pings")
        in keys_called
    )
    assert (
        RedisSchema.Trip.agent_data(event.trip_id, "scoring", "historical_avg")
        in keys_called
    )
    assert (
        RedisSchema.Trip.agent_data(event.trip_id, "support", "trip_context")
        in keys_called
    )
    assert (
        RedisSchema.Trip.agent_data(event.trip_id, "support", "coaching_history")
        in keys_called
    )


@pytest.mark.asyncio
async def test_warm_cache_skips_when_no_agents(orchestrator_mocks):
    orch, fake_redis = orchestrator_mocks
    event = _trip_event("harsh_brake")
    await orch._warm_cache(event, [])
    fake_redis._client.setex.assert_not_awaited()


def test_seal_capsule_includes_device_event_id(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event(
        "harsh_brake",
        device_event_id="DEV-SEAL-42",
    )
    cap = orch._seal_capsule(event, "safety")
    assert cap.device_event_id == "DEV-SEAL-42"
    assert cap.trip_id == event.trip_id
    assert cap.agent == "safety"


@pytest.mark.asyncio
async def test_release_lock_uses_device_event_id_from_capsule():
    import agents.orchestrator.db_manager as dbm_mod
    from agents.base.agent import TDAgentBase

    class StubAgent(TDAgentBase):
        AGENT_NAME = "stub"

        async def _execute(self, trip_id, cache_data):
            return {"ok": True}

        def _get_repos(self):
            return {}

    agent = StubAgent(engine=MagicMock())

    with patch.object(dbm_mod, "DBManager") as MockDB:
        inst = MockDB.return_value
        inst.release_lock = AsyncMock()
        await agent._release_lock("TRP-Xy", "DEV-from-capsule")

    inst.release_lock.assert_awaited_once_with("DEV-from-capsule")


def test_safety_task_calls_asyncio_run():
    import tasks.safety_tasks as safety_tasks

    capsule = {
        "trip_id": "T1",
        "agent": "safety",
        "device_event_id": "",
        "priority": 3,
        "tool_whitelist": [],
        "step_to_tools": {},
        "ttl_seconds": 600,
        "token": None,
    }

    async def fake_run(_capsule):
        return {"status": "success"}

    with patch.object(safety_tasks, "asyncio") as mock_asyncio:
        mock_asyncio.run.side_effect = lambda coro: asyncio.run(coro)
        with patch("tasks.safety_tasks.SafetyAgent") as MockAgent:
            MockAgent.return_value.run = fake_run
            safety_tasks.analyse_event.run(intent_capsule=capsule)

    mock_asyncio.run.assert_called_once()


def test_sentiment_task_calls_asyncio_run():
    import tasks.sentiment_tasks as sentiment_tasks

    capsule = {
        "trip_id": "T1",
        "agent": "sentiment",
        "device_event_id": "",
        "priority": 3,
        "tool_whitelist": [],
        "step_to_tools": {},
        "ttl_seconds": 600,
        "token": None,
    }

    async def fake_run(_capsule):
        return {"status": "success"}

    with patch.object(sentiment_tasks, "asyncio") as mock_asyncio:
        mock_asyncio.run.side_effect = lambda coro: asyncio.run(coro)
        with patch("tasks.sentiment_tasks.SentimentAgent") as MockAgent:
            MockAgent.return_value.run = fake_run
            sentiment_tasks.analyse_feedback.run(intent_capsule=capsule)

    mock_asyncio.run.assert_called_once()


def test_support_task_calls_asyncio_run():
    import tasks.support_tasks as support_tasks

    capsule = {
        "trip_id": "T1",
        "agent": "support",
        "device_event_id": "",
        "priority": 3,
        "tool_whitelist": [],
        "step_to_tools": {},
        "ttl_seconds": 600,
        "token": None,
    }

    async def fake_run(_capsule):
        return {"status": "success"}

    with patch.object(support_tasks, "asyncio") as mock_asyncio:
        mock_asyncio.run.side_effect = lambda coro: asyncio.run(coro)
        with patch("tasks.support_tasks.SupportAgent") as MockAgent:
            MockAgent.return_value.run = fake_run
            support_tasks.generate_coaching.run(intent_capsule=capsule)

    mock_asyncio.run.assert_called_once()
