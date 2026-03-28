import asyncio
import json
import logging

from common.config.settings import get_settings
from common.redis.client import RedisClient
from core.ingestion.sidecar import IngestionSidecar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ingestion")


async def main():
    settings = get_settings()
    redis = RedisClient()
    sidecar = IngestionSidecar(redis)

    logger.info(f"Ingestion worker started. Listening on {settings.ingestion_queue}...")

    try:
        while True:
            # ── Stage 1: Pop from Raw Buffer ──
            # The ingestion_queue is the 'landing zone' for both REST (App) and MQTT (Device)
            # zpopmin ensures we handle CRITICAL severity (score 0) first.
            raw_packet = await redis.pop_from_buffer(settings.ingestion_queue)

            if raw_packet:
                event_type = raw_packet.get("event", {}).get("event_type", "unknown")
                truck_id = raw_packet.get("event", {}).get("truck_id", "unknown")

                logger.info(f"Processing {event_type} for truck {truck_id}")

                # ── The 7-Step Pipeline ──
                success = await sidecar.process_packet(raw_packet)

                if success:
                    logger.info(f"Successfully ingested {event_type}")
                    # Push to visualization buffer (60-min TTL) for observability
                    logger.debug("🔄 Attempting to push to visualization buffer...")
                    try:
                        await redis.push_to_visualization_buffer(
                            json.dumps(raw_packet),
                            ttl=settings.visualization_buffer_ttl,
                        )
                        logger.debug(f"✅ Pushed {event_type} to visualization buffer")
                    except Exception as e:
                        logger.warning(
                            f"❌ Failed to push to visualization buffer: {e}"
                        )
                else:
                    logger.warning(f"Rejected packet for {event_type}")

            else:
                # No events, small sleep to prevent CPU spinning
                await asyncio.sleep(0.1)

    except asyncio.CancelledError:
        logger.info("Ingestion worker stopping...")
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
