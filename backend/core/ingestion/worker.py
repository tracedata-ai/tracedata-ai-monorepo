import asyncio
import logging

from common.redis.client import RedisClient
from common.redis.keys import RedisSchema
from core.ingestion.db import IngestionDB
from core.ingestion.sidecar import IngestionSidecar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ingestion")


async def _discover_trucks(redis: RedisClient) -> list[str]:
    """
    Discover truck IDs from active telemetry buffers in Redis.
    Returns list of truck_ids that have events waiting.

    Pattern: telemetry:{truck_id}:buffer (sorted set)
    """
    pattern = "telemetry:*:buffer"
    keys = await redis._client.keys(pattern)

    # Extract truck_id from "telemetry:{truck_id}:buffer"
    truck_ids = [key.split(":")[1] for key in keys if ":" in key]

    if truck_ids:
        logger.info(
            f"Discovered {len(truck_ids)} trucks with buffered telemetry: {truck_ids}"
        )
    else:
        logger.info(
            "No trucks with buffered telemetry found (scanning empty). Waiting for events..."
        )

    return sorted(set(truck_ids))  # Deduplicate and sort for consistency


async def main():
    logger.info("🚀 Ingestion worker started (dynamic truck discovery mode)")

    async with IngestionDB() as db:
        redis = RedisClient()
        sidecar = IngestionSidecar(db=db, redis=redis)

        try:
            while True:
                # Dynamically discover trucks from Redis keys
                truck_ids = await _discover_trucks(redis)

                if not truck_ids:
                    # No trucks yet — sleep and retry
                    logger.debug("No trucks found, sleeping 1s before retry...")
                    await asyncio.sleep(1.0)
                    continue

                handled = 0

                # Poll all discovered trucks in round-robin
                for truck_id in truck_ids:
                    raw_key = RedisSchema.Telemetry.buffer(truck_id)
                    raw_packet = await redis.pop_from_buffer(raw_key)

                    if raw_packet:
                        event_type = raw_packet.get("event", {}).get(
                            "event_type", "unknown"
                        )
                        truck_id_from_packet = raw_packet.get("event", {}).get(
                            "truck_id", truck_id
                        )

                        logger.info(
                            f"Processing {event_type} for truck {truck_id_from_packet}"
                        )

                        # ── The 7-Step Pipeline ──
                        result = await sidecar.process(
                            raw=raw_packet,
                            truck_id=truck_id_from_packet,
                        )

                        if result.ok:
                            logger.info(
                                f"Successfully ingested {event_type} (trip_id={result.trip_event.trip_id})"
                            )
                        else:
                            logger.warning(f"Rejected packet: {result.reason}")

                        handled += 1

                if handled == 0:
                    # No events, small sleep to prevent CPU spinning
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Ingestion worker stopping...")
        finally:
            await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
