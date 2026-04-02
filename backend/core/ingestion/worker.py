import asyncio
import logging

from common.redis.client import RedisClient
from common.redis.keys import RedisSchema
from core.buffer.ring_buffer import RingBuffer
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
    logger.info("🚀 Ingestion worker started (with ring buffer batching)")

    # Initialize ring buffer for batch processing
    buffer = RingBuffer(
        max_size=100,
        batch_flush_size=10,  # Lower threshold for better responsiveness
        max_wait_seconds=2,  # Shorter timeout for testing
    )

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
                        # Push to ring buffer
                        accepted = await buffer.push(raw_packet)
                        if accepted:
                            handled += 1
                        else:
                            logger.warning(
                                {
                                    "action": "packet_rejected_backpressure",
                                    "truck_id": truck_id,
                                }
                            )

                # Check if buffer should auto-flush
                if await buffer.should_flush():
                    packets = await buffer.flush()
                    logger.info(
                        {
                            "action": "buffer_processing_start",
                            "packets_to_process": len(packets),
                        }
                    )

                    # Process all packets through sidecar
                    for packet in packets:
                        truck_id = packet.get("event", {}).get("truck_id", "unknown")
                        event_type = packet.get("event", {}).get(
                            "event_type", "unknown"
                        )

                        # ── The 7-Step Pipeline ──
                        result = await sidecar.process(
                            raw=packet,
                            truck_id=truck_id,
                        )

                        # Sidecar pushes to processed (success) or rejected (failure); avoid duplicate enqueues.
                        if result.ok:
                            logger.info(
                                {
                                    "action": "batch_item_processed",
                                    "truck_id": truck_id,
                                    "event_type": event_type,
                                    "trip_id": result.trip_event.trip_id,
                                }
                            )
                        else:
                            logger.warning(
                                {
                                    "action": "batch_item_rejected",
                                    "truck_id": truck_id,
                                    "event_type": event_type,
                                    "reason": result.reason,
                                }
                            )

                if handled == 0:
                    # No events, small sleep to prevent CPU spinning
                    await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            logger.info("Ingestion worker stopping...")
        finally:
            await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
