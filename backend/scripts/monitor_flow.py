import asyncio
import os
import sys
import json
from datetime import datetime

# Add app root to path for imports
sys.path.append(os.getcwd())

from common.redis.client import RedisClient
from common.redis.keys import RedisSchema


async def monitor():
    redis = RedisClient()
    truck_id = "TRUCK-SG-1234"
    buffer_key = "td:ingestion:events"
    processed_key = RedisSchema.Telemetry.processed(truck_id)
    rejected_key = RedisSchema.Telemetry.rejected(truck_id)

    print(f"\n--- TraceData Pipeline Monitor (Truck: {truck_id}) ---")
    print(f"Buffer:    {buffer_key}")
    print(f"Processed: {processed_key}")
    print(f"Rejected:  {rejected_key}")
    print("---------------------------------------------------\n")

    try:
        while True:
            # Check Buffer
            raw_count = await redis._client.zcard(buffer_key)
            # Check Processed
            proc_count = await redis._client.zcard(processed_key)
            # Check Rejected
            rej_count = await redis._client.zcard(rejected_key)

            print(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"Buffer: {raw_count} | Processed: {proc_count} | Rejected: {rej_count}",
                end="\r",
            )

            # Peek at latest processed
            if proc_count > 0:
                # We can't pop here, only peek
                latest = await redis._client.zrange(processed_key, 0, 0, withscores=True)
                if latest:
                    event = json.loads(latest[0][0])
                    print(
                        f"\n✨ LATEST PROCESSED: {event['event_type']} (Priority: {event['priority']})"
                    )

            # Peek at latest rejected
            if rej_count > 0:
                latest = await redis._client.zrange(rejected_key, 0, 0, withscores=True)
                if latest:
                    error = json.loads(latest[0][0])
                    print(f"\n❌ LATEST REJECTED: {error['reason']}")

            await asyncio.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        await redis.close()


if __name__ == "__main__":
    asyncio.run(monitor())
