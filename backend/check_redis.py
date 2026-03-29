import asyncio
import os
import sys

# Add app root to path for imports
sys.path.append(os.getcwd())

from common.redis.client import RedisClient


async def check():
    url = os.getenv("REDIS_URL", "NOT_SET")
    print(f"REDIS_URL: {url}")
    redis = RedisClient()
    # redis-py async client properties
    kwargs = redis._client.connection_pool.connection_kwargs
    print(f"Connection Kwargs: {kwargs}")

    # Test ZADD
    await redis._client.flushall()
    res = await redis._client.zadd("td:ingestion:events", mapping={'{"test":1}': 0})
    print(f"ZADD Result: {res}")
    card = await redis._client.zcard("td:ingestion:events")
    print(f"Buffer Card: {card}")

    # Try raw zadd without wrapper
    res2 = await redis._client.execute_command("ZADD", "raw_test", 0, "val")
    print(f"Raw ZADD Result: {res2}")
    print(f"Raw Card: {await redis._client.zcard('raw_test')}")

    # Test ZPOPMIN
    popped = await redis.pop_from_buffer("td:ingestion:events")
    print(f"Popped: {popped}")

    keys = await redis._client.keys("*")
    print(f"Final Keys: {keys}")
    await redis.close()


if __name__ == "__main__":
    asyncio.run(check())
