import asyncio
import logging
import os

from common.config.settings import get_settings
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema
from core.ingestion.db import IngestionDB
from core.ingestion.sidecar import IngestionSidecar

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ingestion")


async def main():
    settings = get_settings()

    # Get truck IDs to monitor from environment or use defaults for dev
    truck_ids_str = os.getenv("TRUCK_IDS", "T001,T002,T003")
    truck_ids = [tid.strip() for tid in truck_ids_str.split(",") if tid.strip()]

    logger.info(f"Ingestion worker started. Monitoring trucks: {truck_ids}")

    async with IngestionDB() as db:
        redis = RedisClient()
        sidecar = IngestionSidecar(db=db, redis=redis)

        try:
            while True:
                handled = 0

                # Poll all trucks in round-robin
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


if __name__ == "__main__":
    asyncio.run(main())
