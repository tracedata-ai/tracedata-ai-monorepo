"""
Tests for RedisClient using fakeredis.

fakeredis provides an in-process Redis server — no Docker required.
Tests cover List (push/pop) and ZSet (zpush/zpop) operations, including
priority ordering which is critical for the ingestion pipeline.
"""

import pytest
import fakeredis.aioredis as fakeredis
from unittest.mock import patch, AsyncMock

from common.redis.client import RedisClient
from common.redis.keys import RedisSchema


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


# ── List (push / pop) ──────────────────────────────────────────────────────────

async def test_push_and_pop_returns_same_value(fake_redis_client):
    """push → pop roundtrip returns the original string."""
    await fake_redis_client.push("td:test:list", "hello")
    result = await fake_redis_client.pop("td:test:list", timeout=1)
    assert result == "hello"


async def test_pop_empty_queue_returns_none(fake_redis_client):
    """pop on an empty queue with timeout returns None."""
    result = await fake_redis_client.pop("td:nonexistent:queue", timeout=1)
    assert result is None


async def test_push_order_is_lifo(fake_redis_client):
    """
    RedisClient uses LPUSH + BRPOP.
    LPUSH pushes to head, BRPOP pops from tail → FIFO order.
    """
    await fake_redis_client.push("td:order:queue", "first")
    await fake_redis_client.push("td:order:queue", "second")

    r1 = await fake_redis_client.pop("td:order:queue", timeout=1)
    r2 = await fake_redis_client.pop("td:order:queue", timeout=1)
    assert r1 == "first"
    assert r2 == "second"


# ── ZSet (zpush / zpop) ────────────────────────────────────────────────────────

async def test_zpush_and_zpop_roundtrip(fake_redis_client):
    """zpush → zpop returns the same member."""
    await fake_redis_client.zpush("td:test:zset", "event-payload", priority=3)
    result = await fake_redis_client.zpop("td:test:zset", timeout=1)
    assert result == "event-payload"


async def test_zpop_empty_zset_returns_none(fake_redis_client):
    """zpop on an empty ZSet returns None."""
    result = await fake_redis_client.zpop("td:nonexistent:zset", timeout=1)
    assert result is None


async def test_zpop_respects_priority_order(fake_redis_client):
    """
    BZPOPMIN returns the member with the LOWEST score first.
    Priority 1 (CRITICAL) < Priority 3 (HIGH) — critical should pop first.
    """
    await fake_redis_client.zpush("td:priority:queue", "event-high", priority=3)
    await fake_redis_client.zpush("td:priority:queue", "event-critical", priority=1)

    first = await fake_redis_client.zpop("td:priority:queue", timeout=1)
    second = await fake_redis_client.zpop("td:priority:queue", timeout=1)

    assert first == "event-critical"   # Score 1 → pops out first
    assert second == "event-high"      # Score 3 → pops out second


# ── String (set_with_ttl / get) ────────────────────────────────────────────────

async def test_set_with_ttl_and_get(fake_redis_client):
    """set_with_ttl stores a value retrievable by get."""
    await fake_redis_client.set_with_ttl("td:trip:T1:context", '{"trip_id": "T1"}', ttl=3600)
    result = await fake_redis_client.get("td:trip:T1:context")
    assert result == '{"trip_id": "T1"}'


async def test_get_missing_key_returns_none(fake_redis_client):
    """get on a non-existent key returns None."""
    result = await fake_redis_client.get("td:doesnotexist")
    assert result is None
