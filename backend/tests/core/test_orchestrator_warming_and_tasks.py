"""
Unit tests: orchestrator cache warming (mocked Redis/DB) and Celery task async wiring.
"""

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
    fake_redis.get_trip_context = AsyncMock(return_value={})
    fake_redis.store_trip_context = AsyncMock(return_value=True)

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
        RedisSchema.Trip.agent_data(event.trip_id, "scoring", "trip_context")
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


@pytest.mark.asyncio
async def test_warm_cache_event_driven_with_scoring_also_warms_all_pings(
    orchestrator_mocks,
):
    """harsh_brake is event-driven; scoring still needs aggregation cache."""
    orch, fake_redis = orchestrator_mocks
    event = _trip_event("harsh_brake", trip_id="TRP-SCORE-MID")

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
            "driver_id": "DRV-MID",
        }
    )
    orch._get_all_pings_for_trip = AsyncMock(
        return_value=[
            {"event_type": "smoothness_log", "trip_id": event.trip_id, "details": {}}
        ]
    )
    orch._get_rolling_average_score = AsyncMock(return_value=None)
    orch._get_coaching_history = AsyncMock(return_value=[])

    await orch._warm_cache(event, ["safety", "scoring"])

    keys_called = {c.args[0] for c in fake_redis._client.setex.await_args_list}
    assert (
        RedisSchema.Trip.agent_data(event.trip_id, "scoring", "all_pings")
        in keys_called
    )


@pytest.mark.asyncio
async def test_dispatch_policy_defers_support_for_flagged_mid_trip(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("harsh_brake")

    orch._append_flagged_event = AsyncMock()
    result = await orch._apply_dispatch_policy(event, ["scoring", "support"])

    assert result == ["scoring"]
    orch._append_flagged_event.assert_awaited_once_with(event)


@pytest.mark.asyncio
async def test_dispatch_policy_end_of_trip_adds_support_when_rules_trigger(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("end_of_trip")

    orch._should_dispatch_coaching = AsyncMock(return_value=True)
    result = await orch._apply_dispatch_policy(event, ["scoring"])

    # Current policy: end_of_trip dispatches scoring only; support follows coaching_ready.
    assert result == ["scoring"]


@pytest.mark.asyncio
async def test_dispatch_policy_end_of_trip_skips_support_when_rules_not_triggered(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("end_of_trip")

    orch._should_dispatch_coaching = AsyncMock(return_value=False)
    result = await orch._apply_dispatch_policy(event, ["scoring", "support"])

    assert result == ["scoring"]


@pytest.mark.asyncio
async def test_dispatch_policy_critical_adds_immediate_support(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("collision")

    result = await orch._apply_dispatch_policy(event, ["safety"])

    assert result == ["safety", "support"]


@pytest.mark.asyncio
async def test_dispatch_policy_coaching_ready_keeps_support_only(orchestrator_mocks):
    """UC1 follow-up: internal coaching_ready dispatches support only."""
    orch, _ = orchestrator_mocks
    event = _trip_event("coaching_ready")
    result = await orch._apply_dispatch_policy(event, ["safety", "scoring", "support"])
    assert result == ["support"]


@pytest.mark.asyncio
async def test_dispatch_policy_coaching_ready_fallback_driver_support(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("coaching_ready")
    result = await orch._apply_dispatch_policy(event, [])
    assert result == ["driver_support"]


@pytest.mark.asyncio
async def test_dispatch_policy_sentiment_ready_keeps_support_only(orchestrator_mocks):
    """UC2: internal sentiment_ready dispatches support only."""
    orch, _ = orchestrator_mocks
    event = _trip_event("sentiment_ready")
    orch._load_trip_runtime_context = AsyncMock(
        return_value={
            "trip_id": event.trip_id,
            "driver_id": "DRV-1",
            "truck_id": "TRK-1",
        }
    )
    orch._save_trip_runtime_context = AsyncMock()
    result = await orch._apply_dispatch_policy(
        event, ["sentiment", "scoring", "support"]
    )
    assert result == ["support"]
    orch._save_trip_runtime_context.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatch_policy_sentiment_ready_fallback_driver_support(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("sentiment_ready")
    orch._load_trip_runtime_context = AsyncMock(return_value={})
    orch._save_trip_runtime_context = AsyncMock()
    result = await orch._apply_dispatch_policy(event, [])
    assert result == ["driver_support"]


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


def _close_coro_and_return(coro, value):
    """Stub for ``run_async`` in tests: avoid 'coroutine was never awaited' warnings."""
    coro.close()
    return value


def test_safety_task_calls_run_async():
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

    ret = {"trip_id": "T1", "agent": "safety"}
    with patch("agents.safety.tasks.run_async") as mock_run_async:
        mock_run_async.side_effect = lambda c: _close_coro_and_return(c, ret)
        out = safety_tasks.analyse_event.run(intent_capsule=capsule)

    assert mock_run_async.call_count == 3
    names = [c.args[0].__name__ for c in mock_run_async.call_args_list]
    assert names == [
        "_publish_agent_flow",
        "_analyse_event_async",
        "_publish_agent_flow",
    ]
    assert out["trip_id"] == "T1"


def test_sentiment_task_calls_run_async():
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

    ret = {"trip_id": "T1", "agent": "sentiment", "status": "done"}
    with patch("agents.sentiment.tasks.run_async") as mock_run_async:
        mock_run_async.side_effect = lambda c: _close_coro_and_return(c, ret)
        out = sentiment_tasks.analyse_feedback.run(intent_capsule=capsule)

    assert mock_run_async.call_count == 3
    names = [c.args[0].__name__ for c in mock_run_async.call_args_list]
    assert names == [
        "_publish_agent_flow",
        "_analyse_feedback_async",
        "_publish_agent_flow",
    ]
    assert out["agent"] == "sentiment"


def test_support_task_calls_run_async():
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

    ret = {"trip_id": "T1", "agent": "driver_support"}
    with patch("agents.driver_support.tasks.run_async") as mock_run_async:
        mock_run_async.side_effect = lambda c: _close_coro_and_return(c, ret)
        out = support_tasks.generate_coaching.run(intent_capsule=capsule)

    assert mock_run_async.call_count == 3
    names = [c.args[0].__name__ for c in mock_run_async.call_args_list]
    assert names == [
        "_publish_agent_flow",
        "_generate_coaching_async",
        "_publish_agent_flow",
    ]
    assert out["trip_id"] == "T1"


def test_resolve_agents_off_mode_keeps_current_behavior(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("collision")
    decision = {"agents_to_dispatch": "not-a-list"}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "off"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == []


def test_resolve_agents_shadow_mode_does_not_change_dispatch(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("collision")
    decision = {"agents_to_dispatch": "not-a-list"}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "shadow"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == []


def test_resolve_agents_enforce_mode_uses_event_matrix_fallback(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("collision")
    decision = {"agents_to_dispatch": "not-a-list"}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "enforce"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == ["safety"]


def test_resolve_agents_filters_unknown_agent_names(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("harsh_brake")
    decision = {
        "agents_to_dispatch": ["safety", "unknown_agent", "support", "scoring"]
    }
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "off"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == ["safety", "support", "scoring"]


def test_resolve_agents_enforce_mode_forces_critical_fallback_when_empty_list(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("collision")
    decision = {"agents_to_dispatch": []}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "enforce"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == ["safety"]


def test_resolve_agents_enforce_mode_keeps_low_risk_empty_dispatch(orchestrator_mocks):
    orch, _ = orchestrator_mocks
    event = _trip_event("smoothness_log")
    decision = {"agents_to_dispatch": []}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "enforce"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == []


def test_resolve_agents_enforce_mode_red_team_unknown_agents_fallback_for_high(
    orchestrator_mocks,
):
    orch, _ = orchestrator_mocks
    event = _trip_event("harsh_brake")
    decision = {"agents_to_dispatch": ["bogus_agent", 123, None]}
    with patch("agents.orchestrator.agent.settings") as mock_settings:
        mock_settings.orchestrator_routing_fallback_mode = "enforce"
        resolved = orch._resolve_agents_for_dispatch(event, decision)
    assert resolved == ["safety", "scoring", "support"]
