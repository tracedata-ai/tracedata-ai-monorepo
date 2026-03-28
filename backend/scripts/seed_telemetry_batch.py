"""
TraceData Backend — Telemetry Batch Seeder.

Populates the ingestion queue with test telemetry events.
These will flow through the pipeline and populate the visualization buffer.

Usage:
    # Seed 5 random events
    python scripts/seed_telemetry_batch.py

    # Seed 20 events with specific types
    python scripts/seed_telemetry_batch.py --count 20 --event-types collision harsh_brake smoothness_log
"""

import asyncio
import json
import random
import uuid
from argparse import ArgumentParser
from datetime import UTC, datetime

from common.config.events import PRIORITY_MAP
from common.models.enums import PingType, Priority, Source
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

# ── Realistic Telemetry Data ────────────────────────────────────────────────

TRUCK_IDS = [
    "TRUCK-SG-1234",
    "TRUCK-SG-5678",
    "TRUCK-SG-9101",
    "TRUCK-JB-2022",
    "TRUCK-KL-3333",
]

DRIVER_IDS = [
    "DRIVER-SG-77",
    "DRIVER-SG-88",
    "DRIVER-SG-99",
    "DRIVER-JB-11",
    "DRIVER-KL-22",
]

TRIP_IDS = [
    "TRIP-LIVE-001",
    "TRIP-LIVE-002",
    "TRIP-LIVE-003",
    "TRIP-LIVE-004",
    "TRIP-LIVE-005",
]

LOCATIONS = [
    {"lat": 1.2863, "lon": 103.8519},  # Marina Bay, Singapore
    {"lat": 1.3521, "lon": 103.8198},  # Raffles, Singapore
    {"lat": 1.2902, "lon": 103.8519},  # Pioneer, Singapore
    {"lat": 1.3424, "lon": 103.7618},  # Changi, Singapore
    {"lat": 1.4454, "lon": 103.7618},  # Lim Chu Kang, Singapore
]

EVENT_TYPES_CONFIG = {
    "collision": {
        "priority": Priority.CRITICAL,
        "details": {
            "impact_severity": random.choice(["low", "medium", "high"]),
            "note": "Vehicle collision detected",
        },
    },
    "rollover": {
        "priority": Priority.CRITICAL,
        "details": {
            "angle_degrees": random.randint(30, 90),
            "note": "Rollover risk detected",
        },
    },
    "driver_sos": {
        "priority": Priority.CRITICAL,
        "details": {"reason": "Manual SOS", "note": "Driver triggered emergency alert"},
    },
    "harsh_brake": {
        "priority": Priority.HIGH,
        "details": {
            "deceleration_g": round(random.uniform(0.7, 1.2), 2),
            "note": "Harsh braking detected",
        },
    },
    "harsh_turn": {
        "priority": Priority.HIGH,
        "details": {
            "lateral_g": round(random.uniform(0.6, 1.0), 2),
            "note": "Harsh turn detected",
        },
    },
    "acceleration": {
        "priority": Priority.MEDIUM,
        "details": {
            "acceleration_g": round(random.uniform(0.5, 0.9), 2),
            "note": "Rapid acceleration",
        },
    },
    "speeding": {
        "priority": Priority.MEDIUM,
        "details": {
            "speed_kmh": random.randint(85, 120),
            "note": "Speed limit exceeded",
        },
    },
    "smoothness_log": {
        "priority": Priority.LOW,
        "details": {
            "smoothness_score": round(random.uniform(0.0, 1.0), 2),
            "note": "Regular smoothness telemetry",
        },
    },
}


async def create_telemetry_payload(event_type: str) -> dict:
    """Generate realistic telemetry payload."""
    config = EVENT_TYPES_CONFIG.get(event_type, EVENT_TYPES_CONFIG["smoothness_log"])
    priority = config["priority"]

    event_id = str(uuid.uuid4())
    device_event_id = f"DEV-{event_type[:2].upper()}-{str(uuid.uuid4())[:8]}"
    truck_id = random.choice(TRUCK_IDS)
    trip_id = random.choice(TRIP_IDS)
    driver_id = random.choice(DRIVER_IDS)
    location = random.choice(LOCATIONS)

    payload = {
        "ping_type": PingType.BATCH,
        "source": Source.TELEMATICS_DEVICE,
        "is_emergency": priority == Priority.CRITICAL,
        "event": {
            "event_id": event_id,
            "device_event_id": device_event_id,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "event_type": event_type,
            "category": "adhoc",
            "priority": priority.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": random.randint(0, 3600),
            "trip_meter_km": round(random.uniform(0.1, 50.0), 1),
            "odometer_km": round(random.uniform(100000, 200000), 1),
            "location": location,
            "details": config["details"],
        },
    }

    return payload


async def seed_telemetry(event_types: list[str], count: int = 1) -> None:
    """
    Seed `count` telemetry events of specified types into the ingestion queue.
    """
    redis = RedisClient()

    print("\n📡 TraceData Telemetry Batch Seeder")
    print(f"   Total Events: {count}")
    print(f"   Event Types: {', '.join(event_types)}\n")

    seeded_count = 0
    for i in range(count):
        event_type = random.choice(event_types)
        payload = await create_telemetry_payload(event_type)
        config = EVENT_TYPES_CONFIG[event_type]
        priority = config["priority"]
        score = PRIORITY_MAP.get(priority, 9)

        truck_id = payload["event"]["truck_id"]
        trip_id = payload["event"]["trip_id"]
        buffer_key = RedisSchema.Telemetry.buffer(truck_id)

        try:
            await redis.push_to_buffer(buffer_key, json.dumps(payload), score)
            seeded_count += 1

            status = "✅"
            print(
                f"{status} [{i+1:3d}] {event_type:20s} | "
                f"Priority: {priority.value:8s} | Truck: {truck_id} | Trip: {trip_id}"
            )
        except Exception as e:
            print(f"❌ [{i+1:3d}] Failed to seed {event_type}: {e}")

    print(f"\n✨ Seeded {seeded_count}/{count} events into per-truck buffers")
    print("\n📝 Next steps:")
    print("   1. Run the ingestion worker:  python -m core.ingestion.worker")
    print("   2. Check Redis Insights → td → visualization → recent_events")
    print("   3. Events should appear with 60-minute TTL\n")

    await redis.close()


async def main():
    parser = ArgumentParser(
        description="Seed telemetry events into the ingestion queue for testing and observability.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of events to seed (default: 5)",
    )
    parser.add_argument(
        "--event-types",
        nargs="+",
        default=list(EVENT_TYPES_CONFIG.keys()),
        help=f"Event types to seed (default: all). Options: {', '.join(EVENT_TYPES_CONFIG.keys())}",
    )

    args = parser.parse_args()

    # Validate event types
    invalid_types = set(args.event_types) - set(EVENT_TYPES_CONFIG.keys())
    if invalid_types:
        print(f"❌ Invalid event types: {', '.join(invalid_types)}")
        print(f"   Valid types: {', '.join(EVENT_TYPES_CONFIG.keys())}")
        return

    await seed_telemetry(args.event_types, args.count)


if __name__ == "__main__":
    asyncio.run(main())
