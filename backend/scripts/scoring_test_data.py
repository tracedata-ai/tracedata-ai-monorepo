"""
Complete trips telemetry generator for multi-truck, multi-trip scenarios.

Sends START → SMOOTHNESS_LOG (10-min batch stats) → END_OF_TRIP events for:
  - 5 trucks (TK001 - TK005)
  - 10 trips per truck (to and fro)
  - 3 events per trip (START, smoothness batch, END)
  - Total: 150 events

Usage:
  REDIS_URL=redis://localhost:6379/0 python scripts/scoring_test_data.py
"""

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime, timedelta

import redis.asyncio as redis

from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    smoothness_details_mild_variant,
)

REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


async def send_complete_trips_multi_truck():
    """Send 5 trucks × 10 trips × 3 events = 150 complete trip events."""

    # Configuration
    TRUCKS = ["TK001", "TK002", "TK003", "TK004", "TK005"]
    DRIVERS = [
        "DRV-ANON-D1",
        "DRV-ANON-D2",
        "DRV-ANON-D3",
        "DRV-ANON-D4",
        "DRV-ANON-D5",
    ]
    TRIPS_PER_TRUCK = 10

    # Base locations for to/fro trips
    LOCATIONS = {
        "start": {"lat": 1.2800, "lon": 103.8400},
        "end": {"lat": 1.3400, "lon": 103.8600},
    }

    r = await redis.from_url(REDIS_URL)

    try:
        for tid in TRUCKS:
            await r.delete(f"telemetry:{tid}:buffer")

        event_counter = 0
        trips_created = 0
        base_time = datetime.now(UTC)

        print("\n" + "=" * 70)
        print("[SEND] COMPLETE TRIPS: 5 TRUCKS x 10 TRIPS x 3 EVENTS")
        print("=" * 70)

        for truck_idx, truck_id in enumerate(TRUCKS):
            for trip_num in range(TRIPS_PER_TRUCK):
                driver_id = DRIVERS[trip_num % len(DRIVERS)]

                # Generate fully unique IDs using full UUIDs with readable prefixes
                # Format (fits database column limits):
                #   - trip_id: TRIP-ID-{uuid}        (43 chars, fits 100-char column)
                #   - event_id: {uuid}               (36 chars, fits 36-char column - no room for prefix)
                #   - device_event_id: DEVICE-ID-{uuid} (45 chars, fits 50-char column)
                trip_id = f"TRIP-ID-{uuid.uuid4()}"
                start_event_id = str(uuid.uuid4())
                normal_event_id = str(uuid.uuid4())
                end_event_id = str(uuid.uuid4())

                # Trip duration and distance vary
                trip_duration_minutes = 45 + (trip_num * 3) % 30
                trip_distance_km = 25 + (trip_num * 2) % 40

                # Alternate between forward and return trips
                is_return_trip = trip_num % 2 == 1
                start_location = (
                    LOCATIONS["end"] if is_return_trip else LOCATIONS["start"]
                )
                end_location = (
                    LOCATIONS["start"] if is_return_trip else LOCATIONS["end"]
                )

                trip_start = base_time + timedelta(hours=(truck_idx * 50 + trip_num))
                start_odometer = 100000 + (truck_idx * 10000) + (trip_num * 500)

                # ─── START OF TRIP
                start_event = {
                    "ping_type": "start_of_trip",
                    "source": "driver_app",
                    "is_emergency": False,
                    "event": {
                        "event_id": start_event_id,
                        "device_event_id": f"DEVICE-ID-{uuid.uuid4()}",
                        "trip_id": trip_id,
                        "truck_id": truck_id,
                        "driver_id": driver_id,
                        "event_type": "start_of_trip",
                        "category": "trip_lifecycle",
                        "priority": "low",
                        "timestamp": trip_start.isoformat(),
                        "offset_seconds": 0,
                        "trip_meter_km": 0.0,
                        "odometer_km": float(start_odometer),
                        "lat": start_location["lat"],
                        "lon": start_location["lon"],
                        "details": {
                            "odometer_km": start_odometer,
                            "fuel_level_litres": 50 + (trip_num % 10),
                            "vehicle_status": "ready",
                            "trip_direction": "return" if is_return_trip else "forward",
                        },
                        "schema_version": "event_v1",
                    },
                }
                buffer_key = f"telemetry:{truck_id}:buffer"
                json_str = json.dumps(start_event)
                await r.zadd(buffer_key, {json_str: event_counter})
                event_counter += 1

                # ─── 1Hz / 10-min smoothness batch (positive reinforcement layer)
                mid_time = trip_start + timedelta(minutes=trip_duration_minutes // 2)
                mid_odometer = start_odometer + int(trip_distance_km / 2)
                mid_lat = (start_location["lat"] + end_location["lat"]) / 2
                mid_lon = (start_location["lon"] + end_location["lon"]) / 2

                smooth_event = build_smoothness_log_packet(
                    trip_id=trip_id,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    timestamp=mid_time,
                    offset_seconds=int((trip_duration_minutes // 2) * 60),
                    trip_meter_km=trip_distance_km / 2,
                    odometer_km=float(mid_odometer),
                    lat=mid_lat,
                    lon=mid_lon,
                    batch_id=f"BATCH-{truck_id}-{trip_id[:24]}-m{trip_num}",
                    event_id=normal_event_id,
                    device_event_id=f"DEVICE-ID-{uuid.uuid4()}",
                    details=smoothness_details_mild_variant(
                        trip_num + truck_idx * 100
                    ),
                )
                json_str = json.dumps(smooth_event)
                await r.zadd(buffer_key, {json_str: event_counter})
                event_counter += 1

                # ─── END OF TRIP
                end_time = trip_start + timedelta(minutes=trip_duration_minutes)
                end_odometer = start_odometer + int(trip_distance_km)

                end_event = {
                    "ping_type": "end_of_trip",
                    "source": "driver_app",
                    "is_emergency": False,
                    "event": {
                        "event_id": end_event_id,
                        "device_event_id": f"DEVICE-ID-{uuid.uuid4()}",
                        "trip_id": trip_id,
                        "truck_id": truck_id,
                        "driver_id": driver_id,
                        "event_type": "end_of_trip",
                        "category": "trip_lifecycle",
                        "priority": "low",
                        "timestamp": end_time.isoformat(),
                        "offset_seconds": trip_duration_minutes * 60,
                        "trip_meter_km": trip_distance_km,
                        "odometer_km": float(end_odometer),
                        "lat": end_location["lat"],
                        "lon": end_location["lon"],
                        "details": {
                            "duration_minutes": trip_duration_minutes,
                            "distance_km": trip_distance_km,
                            "safety_percentage": 85 + (trip_num % 10),
                            "fuel_consumed_litres": 5.0 + (trip_num * 0.2),
                            "trip_direction": "return" if is_return_trip else "forward",
                        },
                        "schema_version": "event_v1",
                    },
                }
                json_str = json.dumps(end_event)
                await r.zadd(buffer_key, {json_str: event_counter})
                event_counter += 1

                trips_created += 1

                # Progress indicator every truck
                if (trip_num + 1) % 5 == 0:
                    print(
                        f"   - {truck_id}: {trip_num + 1}/{TRIPS_PER_TRUCK} trips queued ({(trip_num + 1) * 3} events)"
                    )

        print("\n" + "=" * 70)
        print("[OK] COMPLETE TRIPS TELEMETRY SENT TO REDIS")
        print("=" * 70)
        print(
            f"Queues:              telemetry:{{truck_id}}:buffer ({', '.join(TRUCKS)})"
        )
        print(f"Trucks:              {len(TRUCKS)} ({', '.join(TRUCKS)})")
        print(f"Trips per truck:     {TRIPS_PER_TRUCK}")
        print("Events per trip:     3 (START, NORMAL_OP, END)")
        print("Trip directions:     To and Fro (alternating)")
        print(f"\nTotal trips created: {trips_created}")
        print(f"Total events queued: {event_counter}")
        print("=" * 70)
        print("\n[INFO] Expected pipeline flow:")
        print("   1. Ingestion sidecar validates and stores in pipeline_events")
        print("   2. Orchestrator processes START events -> creates pipeline_trips")
        print("   3. Orchestrator processes smoothness_log events -> trip analytics")
        print("   4. Orchestrator processes END events -> triggers scoring agent")
        print(
            "   5. Scoring worker calculates trip score -> writes back to pipeline_trips"
        )
        print("=" * 70 + "\n")

    finally:
        await r.aclose()


async def main():
    await send_complete_trips_multi_truck()


if __name__ == "__main__":
    asyncio.run(main())
