import asyncio
import logging

from common.config.settings import get_settings
from common.redis.client import RedisClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion")


async def main():
    settings = get_settings()
    redis = RedisClient()
    logger.info(f"Ingestion worker started. Listening on {settings.ingestion_queue}")

    try:
        while True:
            # ── Role 2 — Priority Popping (as per Flight Plan) ──
            # Use zpop to pick up the highest priority event (lowest score)
            event = await redis.zpop(settings.ingestion_queue, timeout=5)
            if event:
                logger.info(f"Ingested priority event: {event[:100]}...")
                # Push to orchestrator (Standard List)
                await redis.push(settings.orchestrator_queue, event)
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
