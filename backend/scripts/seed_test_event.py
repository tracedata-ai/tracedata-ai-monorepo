import asyncio
import json
import os
import sys
import uuid
from datetime import UTC, datetime

import redis.asyncio as redis

# Add app root to path for imports
sys.path.append(os.getcwd())

# Import schema for queue names
from common.redis.keys import RedisSchema


async def seed():
    redis_host = os.getenv("REDIS_HOST", "localhost")
    print(f"Connecting to Redis at {redis_host}:6379...")
    try:
        r = redis.Redis(host=redis_host, port=6379, decode_responses=True)
        await r.ping()
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        return

    event_id = str(uuid.uuid4())
    trip_id = "TRIP-TEST-001"

    # Payload matching common.models.events.TelemetryPacket
    payload = {
        "ping_type": "high_speed",
        "source": "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id": event_id,
            "device_event_id": "DEV-HB-001",
            "trip_id": trip_id,
            "truck_id": "TRUCK-101",
            "driver_id": "DRIVER-77",
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
            "location": {"lat": 1.2863, "lon": 103.8519},
            "details": {"g_force": -0.85, "speed_kmh": 85},
        },
    }

    # ── Role 1 — Priority Event Buffer (as per Flight Plan) ──
    # We push into the ingestion queue (ZSet) with priority 3 (HIGH)
    await r.zadd(RedisSchema.INGESTION_QUEUE, {json.dumps(payload): 3})

    print(
        f"Successfully seeded harsh_brake event (Priority 3) into {RedisSchema.INGESTION_QUEUE}"
    )
    print(f"Event ID: {event_id}")

    await r.close()


if __name__ == "__main__":
    asyncio.run(seed())
