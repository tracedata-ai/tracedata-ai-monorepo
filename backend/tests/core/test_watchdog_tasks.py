from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tasks import watchdog_tasks


def test_reset_stuck_events_invokes_db_watchdog():
    async def fake_watchdog():
        return None

    with patch.object(watchdog_tasks, "DBManager") as MockDB:
        MockDB.return_value.watchdog = fake_watchdog
        result = watchdog_tasks.reset_stuck_events.run()

    assert result["status"] == "ok"
    assert result["task"] == "reset_stuck_events"


@pytest.mark.asyncio
async def test_collect_queue_sizes_prefers_zcard_then_llen():
    class DummyRedis:
        pass

    redis = DummyRedis()
    redis._client = AsyncMock()

    async def zcard_side_effect(key):
        return 2 if key == "td:ingestion:events" else 0

    async def llen_side_effect(_key):
        return 5

    redis._client.zcard.side_effect = zcard_side_effect
    redis._client.llen.side_effect = llen_side_effect

    sizes = await watchdog_tasks._collect_queue_sizes(redis)

    assert sizes["td:ingestion:events"] == 2
    assert sizes["td:agent:safety"] == 5


def test_publish_queue_depths_calls_collector():
    with (
        patch.object(watchdog_tasks, "RedisClient") as MockRedis,
        patch.object(
            watchdog_tasks, "_collect_queue_sizes", new=AsyncMock()
        ) as collector,
        patch.object(
            watchdog_tasks, "_publish_worker_health", new=AsyncMock()
        ) as publish_health,
    ):
        collector.return_value = {"td:agent:safety": 1}
        MockRedis.return_value = MagicMock()
        result = watchdog_tasks.publish_queue_depths.run()

    collector.assert_awaited_once()
    publish_health.assert_awaited_once()
    assert publish_health.await_args[0][1] == {"td:agent:safety": 1}
    assert result["status"] == "ok"
    assert result["task"] == "publish_queue_depths"
    assert result["queues"]["td:agent:safety"] == 1
