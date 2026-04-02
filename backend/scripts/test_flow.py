#!/usr/bin/env python
"""Quick test of one fresh trip through the entire pipeline."""

import asyncio
import json
import uuid
from datetime import UTC, datetime, timedelta

import redis.asyncio as redis

from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    smoothness_details_mild_variant,
)


async def send_one_trip():
    """Send a single fresh trip with unique IDs."""
    r = await redis.from_url("redis://localhost:6379/0")

    try:
        # Clear old data
        await r.delete("telemetry:TK001:buffer")

        trip_id = f"trip-test-{str(uuid.uuid4())[:8]}"
        truck_id = "TK001"
        driver_id = "DRV-TEST-001"
        base_time = datetime.now(UTC)
        event_counter = 0

        events = []

        # START
        start_event = {
            "ping_type": "start_of_trip",
            "source": "driver_app",
            "is_emergency": False,
            "event": {
                "event_id": f"evt-start-{str(uuid.uuid4())[:6]}",
                "device_event_id": f"DEV-START-{str(uuid.uuid4())[:6]}",
                "trip_id": trip_id,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "event_type": "start_of_trip",
                "category": "trip_lifecycle",
                "priority": "low",
                "timestamp": base_time.isoformat(),
                "offset_seconds": 0,
                "trip_meter_km": 0.0,
                "odometer_km": 180000.0,
                "location": {"lat": 1.2800, "lon": 103.8400},
                "details": {
                    "odometer_km": 180000,
                    "fuel_level_litres": 45,
                    "vehicle_status": "ready",
                },
                "schema_version": "event_v1",
            },
        }
        json_str = json.dumps(start_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1
        events.append("START")

        # 10-min smoothness batch (edge stats → scoring input)
        smooth_event = build_smoothness_log_packet(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            timestamp=base_time + timedelta(minutes=15),
            offset_seconds=900,
            trip_meter_km=7.5,
            odometer_km=180007.5,
            lat=1.2810,
            lon=103.8410,
            batch_id=f"BATCH-{truck_id}-flowtest",
            event_id=f"evt-smooth-{str(uuid.uuid4())[:6]}",
            device_event_id=f"DEV-SMOOTH-{str(uuid.uuid4())[:6]}",
            details=smoothness_details_mild_variant(1),
        )
        json_str = json.dumps(smooth_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1
        events.append("SMOOTHNESS")

        # END OF TRIP
        end_event = {
            "ping_type": "end_of_trip",
            "source": "driver_app",
            "is_emergency": False,
            "event": {
                "event_id": f"evt-end-{str(uuid.uuid4())[:6]}",
                "device_event_id": f"DEV-END-{str(uuid.uuid4())[:6]}",
                "trip_id": trip_id,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "event_type": "end_of_trip",
                "category": "trip_lifecycle",
                "priority": "low",
                "timestamp": (base_time + timedelta(minutes=30)).isoformat(),
                "offset_seconds": 1800,
                "trip_meter_km": 15.0,
                "odometer_km": 180015.0,
                "location": {"lat": 1.2900, "lon": 103.8500},
                "details": {
                    "duration_minutes": 30,
                    "distance_km": 15.0,
                    "safety_percentage": 92,
                },
                "schema_version": "event_v1",
            },
        }
        json_str = json.dumps(end_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1
        events.append("END")

        print("[TEST] One fresh trip queued:")
        print(f"  Trip ID: {trip_id}")
        print(f"  Events: {' -> '.join(events)}")
        print(f"  Queue: telemetry:TK001:buffer ({event_counter} events)")

    finally:
        await r.aclose()


if __name__ == "__main__":
    asyncio.run(send_one_trip())
