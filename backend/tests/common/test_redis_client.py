from unittest.mock import patch

import fakeredis.aioredis as fakeredis
import pytest

from common.redis.client import RedisClient


@pytest.fixture
async def fake_redis_client():
    """
    A RedisClient backed by a fakeredis server instead of a real one.
    Patches `redis.from_url` so RedisClient.__init__ gets the fake.
    """
    server = fakeredis.FakeRedis(decode_responses=True)
    with patch("common.redis.client.redis.from_url", return_value=server):
        client = RedisClient()
    yield client
    await server.aclose()


# ── Pipeline Queues (ZSets) ──────────────────────────────────────────────


async def test_buffer_push_and_pop_returns_same_value(fake_redis_client):
    """push_to_buffer → pop_from_buffer roundtrip returns dict."""
    payload = {"event": "test"}
    await fake_redis_client.push_to_buffer("td:test:buffer", '{"event": "test"}', score=9)
    result = await fake_redis_client.pop_from_buffer("td:test:buffer")
    assert result == payload


async def test_buffer_pop_respects_priority_order(fake_redis_client):
    """
    zpopmin returns the member with the LOWEST score first.
    Score 0 (CRITICAL) < Score 9 (LOW).
    """
    await fake_redis_client.push_to_buffer("td:test:buffer", '{"ev": "low"}', score=9)
    await fake_redis_client.push_to_buffer("td:test:buffer", '{"ev": "critical"}', score=0)

    first = await fake_redis_client.pop_from_buffer("td:test:buffer")
    second = await fake_redis_client.pop_from_buffer("td:test:buffer")

    assert first == {"ev": "critical"}
    assert second == {"ev": "low"}


async def test_processed_push_and_pop(fake_redis_client):
    """push_to_processed → pop_from_processed works."""
    payload = {"event": "processed"}
    await fake_redis_client.push_to_processed("td:test:proc", '{"event": "processed"}', score=3)
    result = await fake_redis_client.pop_from_processed("td:test:proc")
    assert result == payload


# ── Agent Working Cache (Strings/JSON/Lists) ─────────────────────────────


async def test_trip_context_store_and_get(fake_redis_client):
    """store_trip_context and get_trip_context work with JSON."""
    ctx = {"trip_id": "T1", "status": "active"}
    await fake_redis_client.store_trip_context("td:trip:T1:context", ctx, ttl=60)
    result = await fake_redis_client.get_trip_context("td:trip:T1:context")
    assert result == ctx


async def test_smoothness_logs_accumulation(fake_redis_client):
    """push_smoothness_log appends to list and get_all_smoothness_logs reads all."""
    l1 = {"window": 1}
    l2 = {"window": 2}

    await fake_redis_client.push_smoothness_log("td:trip:T1:logs", l1, ttl=60)
    await fake_redis_client.push_smoothness_log("td:trip:T1:logs", l2, ttl=60)

    all_logs = await fake_redis_client.get_all_smoothness_logs("td:trip:T1:logs")
    # LPUSH makes it [l2, l1]
    assert len(all_logs) == 2
    assert all_logs == [l2, l1]


# ── Completion Signalling (Pub/Sub + List) ───────────────────────────────


async def test_publish_completion_writes_to_list(fake_redis_client):
    """publish_completion writes the event to the durable list."""
    event = {"agent": "safety", "done": True}
    # We can't easily test Pub/Sub with fakeredis in a single-threaded test
    # but we can verify it writes to the fallback list.
    await fake_redis_client.publish_completion("td:trip:T1:events", event, ttl=60)

    # Re-use get_all_smoothness_logs logic to check the list
    raw_list = await fake_redis_client._client.lrange("td:trip:T1:events", 0, -1)
    assert len(raw_list) == 1
    import json
    assert json.loads(raw_list[0]) == event
