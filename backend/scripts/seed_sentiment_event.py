"""
TraceData Backend - Sentiment Event Seeder.

Seeds sentiment-focused telemetry events into Redis buffer so the pipeline
reliably routes to Orchestrator -> Sentiment Agent.

Usage:
    python -m scripts.seed_sentiment_event
    python -m scripts.seed_sentiment_event --count 3 --event-type driver_feedback
"""

import asyncio
import json
import uuid
from argparse import ArgumentParser
from datetime import UTC, datetime

from common.config.events import EVENT_MATRIX, PRIORITY_MAP
from common.models.enums import PingType, Source
from common.redis.client import RedisClient
from common.redis.keys import RedisSchema

SENTIMENT_EVENT_TYPES = {
    "driver_dispute",
    "driver_complaint",
    "driver_feedback",
    "driver_comment",
}


def _build_payload(
    event_type: str,
    truck_id: str,
    trip_id: str,
    driver_id: str,
    message: str,
) -> dict:
    config = EVENT_MATRIX[event_type]

    return {
        "ping_type": PingType.BATCH,
        "source": Source.TELEMATICS_DEVICE,
        "is_emergency": False,
        "event": {
            "event_id": str(uuid.uuid4()),
            "device_event_id": f"DEV-SENT-{str(uuid.uuid4())[:8]}",
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "event_type": event_type,
            "category": config.category,
            "priority": config.priority.value,
            "timestamp": datetime.now(UTC).isoformat(),
            "offset_seconds": 10,
            "trip_meter_km": 1.2,
            "odometer_km": 123456.7,
            "location": {"lat": 1.30, "lon": 103.80},
            "details": {
                "message": message,
                "feedback_channel": "manual_seed",
            },
            "schema_version": "event_v1",
        },
    }


async def seed_sentiment_events(
    count: int,
    event_type: str,
    truck_id: str,
    driver_id: str,
    fixed_trip_id: str | None,
    message: str,
) -> None:
    redis = RedisClient()

    config = EVENT_MATRIX[event_type]
    score = PRIORITY_MAP.get(config.priority, 9)

    print("\n[seed_sentiment_event] starting")
    print(f"  count: {count}")
    print(f"  event_type: {event_type}")
    print(f"  truck_id: {truck_id}")
    print(f"  driver_id: {driver_id}")
    print(f"  priority: {config.priority.value}\n")

    for i in range(count):
        trip_id = fixed_trip_id or f"TRIP-SENT-{str(uuid.uuid4())[:8]}"
        payload = _build_payload(event_type, truck_id, trip_id, driver_id, message)
        key = RedisSchema.Telemetry.buffer(truck_id)

        await redis.push_to_buffer(key, json.dumps(payload), score)

        print(
            f"  ok [{i+1}/{count}] key={key} trip_id={trip_id} device_event_id={payload['event']['device_event_id']}"
        )

    await redis.close()
    print("\n[seed_sentiment_event] done")
    print("  Next:")
    print("  1) docker compose logs orchestrator | grep dispatch")
    print("  2) docker compose logs sentiment_worker | grep intent_capsule_received")


async def main() -> None:
    parser = ArgumentParser(
        description="Seed sentiment events into telemetry buffer for stable sentiment-agent routing.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="How many sentiment events to seed.",
    )
    parser.add_argument(
        "--event-type",
        type=str,
        default="driver_feedback",
        choices=sorted(SENTIMENT_EVENT_TYPES),
        help="Sentiment event type to seed.",
    )
    parser.add_argument(
        "--truck-id",
        type=str,
        default="TRUCK-SENTIMENT-001",
        help="Truck id to route into telemetry buffer.",
    )
    parser.add_argument(
        "--driver-id",
        type=str,
        default="DRIVER-SENTIMENT-001",
        help="Driver id used in payload.",
    )
    parser.add_argument(
        "--trip-id",
        type=str,
        default=None,
        help="Optional fixed trip id. If omitted, each event gets a unique trip id.",
    )
    parser.add_argument(
        "--message",
        type=str,
        default="driver says brake alert is too sensitive",
        help="Feedback text in event.details.message.",
    )

    args = parser.parse_args()

    await seed_sentiment_events(
        count=args.count,
        event_type=args.event_type,
        truck_id=args.truck_id,
        driver_id=args.driver_id,
        fixed_trip_id=args.trip_id,
        message=args.message,
    )


if __name__ == "__main__":
    asyncio.run(main())
