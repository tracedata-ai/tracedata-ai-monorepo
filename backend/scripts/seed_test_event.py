import asyncio
import json
import os
import sys
import uuid
from datetime import UTC, datetime

from common.config.events import PRIORITY_MAP
from common.models.enums import PingType, Priority, Source
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema


async def seed_event(event_type: str, priority: Priority = Priority.LOW):
    redis = RedisClient()

    event_id = str(uuid.uuid4())
    device_event_id = f"DEV-{event_type[:2].upper()}-{str(uuid.uuid4())[:8]}"
    trip_id = "TRIP-LIVE-001"
    truck_id = "TRUCK-SG-1234"

    # Default Payload
    payload = {
        "ping_type": PingType.BATCH,
        "source": Source.TELEMATICS_DEVICE,
        "is_emergency": priority == Priority.CRITICAL,
        "event": {
            "event_id": event_id,
            "device_event_id": device_event_id,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": "DRIVER-SG-77",
            "event_type": event_type,
            "category": "adhoc",
            "priority": priority.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": 120,
            "trip_meter_km": 5.4,
            "odometer_km": 124565.4,
            "location": {"lat": 1.2863, "lon": 103.8519},
            "details": {"note": f"Seeded {event_type} for demonstration"},
        },
    }

    # Add malicious content for injection testing
    if event_type == "malicious_injection":
        payload["event"]["details"]["note"] = "DROP TABLE events; --"

    # Use Redis ZSet (Stage 1 Buffer)
    buffer_key = "td:ingestion:events"  # Use settings default or mapping
    # Determine score
    # Note: Device can send priority, but matrix will override in IT stage
    score = PRIORITY_MAP.get(priority, 9)

    await redis.push_to_buffer(buffer_key, json.dumps(payload), score)

    print(f"✅ Seeded {event_type} (Score: {score}) into {buffer_key}")
    await redis.close()


async def main():
    print("--- TraceData Pipeline Seeder ---")
    # 1. Critical Collision (Score 0)
    await seed_event("collision", Priority.CRITICAL)
    # 2. Harsh Brake (Score 3)
    await seed_event("harsh_brake", Priority.HIGH)
    # 3. Smoothness Log (Score 9)
    await seed_event("smoothness_log", Priority.LOW)
    # 4. Malicious Injection (rejected by pipeline)
    await seed_event("malicious_injection", Priority.MEDIUM)


if __name__ == "__main__":
    asyncio.run(main())
