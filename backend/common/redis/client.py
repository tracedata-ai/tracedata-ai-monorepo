import redis.asyncio as redis

from common.config.settings import get_settings

settings = get_settings()


class RedisClient:
    """Async Redis client wrapper for TraceData."""

    def __init__(self):
        self._client = redis.from_url(settings.redis_url, decode_responses=True)

    async def push(self, queue_name: str, data: str):
        """Push data to the tail of a list (LPUSH)."""
        await self._client.lpush(queue_name, data)

    async def zpush(self, queue_name: str, data: str, priority: int):
        """Push data to a sorted set (ZADD)."""
        await self._client.zadd(queue_name, {data: priority})

    async def pop(self, queue_name: str, timeout: int = 0):
        """Blocking pop from the head of a list (BRPOP)."""
        # brpop returns (key, value)
        result = await self._client.brpop(queue_name, timeout=timeout)
        return result[1] if result else None

    async def zpop(self, queue_name: str, timeout: int = 0):
        """Blocking pop from a sorted set (BZPOPMIN)."""
        # bzpopmin returns (key, member, score)
        result = await self._client.bzpopmin(queue_name, timeout=timeout)
        return result[1] if result else None

    async def set_with_ttl(self, key: str, value: str, ttl: int):
        """Set a key with an expiration time."""
        await self._client.setex(key, ttl, value)

    async def get(self, key: str):
        """Get a key's value."""
        return await self._client.get(key)

    async def close(self):
        """Close the Redis connection."""
        await self._client.close()
