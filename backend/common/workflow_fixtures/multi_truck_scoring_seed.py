"""
Multi-truck Redis buffer seed: 5 trucks × 10 trips × 3 packets (start, smoothness, end).

Used for load-style E2E (many trips scoring). Not a single ``play_workflow`` queue:
each truck has its own ``telemetry:{truck}:buffer`` ZSET.

See ``scripts/push_multi_truck_scoring_seed.py`` and ``docs/workflow_testing.md``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import redis.asyncio as redis
from pydantic import TypeAdapter

from common.models.events import TelemetryPacket
from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    smoothness_details_mild_variant,
)

TRUCKS = ["TK001", "TK002", "TK003", "TK004", "TK005"]
DRIVERS = [
    "DRV-ANON-D1",
    "DRV-ANON-D2",
    "DRV-ANON-D3",
    "DRV-ANON-D4",
    "DRV-ANON-D5",
]
LOCATIONS = {
    "start": {"lat": 1.28, "lon": 103.84},
    "end": {"lat": 1.34, "lon": 103.86},
}


def _dump_packet(raw: dict[str, Any]) -> str:
    return TypeAdapter(TelemetryPacket).validate_python(raw).model_dump_json()


async def push_multi_truck_scoring_seed(
    *,
    redis_url: str,
    trips_per_truck: int = 10,
) -> dict[str, Any]:
    """
    Clear buffers for TRUCKS, then ZADD start → smoothness → end for each trip.

    Returns summary dict for logging.
    """
    r = redis.from_url(redis_url, decode_responses=True)

    try:
        for tid in TRUCKS:
            await r.delete(f"telemetry:{tid}:buffer")

        event_counter = 0
        trips_created = 0
        base_time = datetime.now(UTC)

        for truck_idx, truck_id in enumerate(TRUCKS):
            for trip_num in range(trips_per_truck):
                driver_id = DRIVERS[trip_num % len(DRIVERS)]
                trip_id = f"TRIP-ID-{uuid.uuid4()}"
                start_event_id = str(uuid.uuid4())
                normal_event_id = str(uuid.uuid4())
                end_event_id = str(uuid.uuid4())

                trip_duration_minutes = 45 + (trip_num * 3) % 30
                trip_distance_km = 25 + (trip_num * 2) % 40
                is_return_trip = trip_num % 2 == 1
                start_loc = LOCATIONS["end"] if is_return_trip else LOCATIONS["start"]
                end_loc = LOCATIONS["start"] if is_return_trip else LOCATIONS["end"]

                trip_start = base_time + timedelta(hours=(truck_idx * 50 + trip_num))
                start_odometer = 100000 + (truck_idx * 10000) + (trip_num * 500)
                buffer_key = f"telemetry:{truck_id}:buffer"

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
                        "timestamp": trip_start.isoformat().replace("+00:00", "Z"),
                        "offset_seconds": 0,
                        "trip_meter_km": 0.0,
                        "odometer_km": float(start_odometer),
                        "location": {
                            "lat": start_loc["lat"],
                            "lon": start_loc["lon"],
                        },
                        "details": {
                            "odometer_km": start_odometer,
                            "fuel_level_litres": 50 + (trip_num % 10),
                            "vehicle_status": "ready",
                            "trip_direction": "return" if is_return_trip else "forward",
                        },
                        "schema_version": "event_v1",
                    },
                }
                await r.zadd(buffer_key, {_dump_packet(start_event): event_counter})
                event_counter += 1

                mid_time = trip_start + timedelta(minutes=trip_duration_minutes // 2)
                mid_odometer = start_odometer + int(trip_distance_km / 2)
                mid_lat = (start_loc["lat"] + end_loc["lat"]) / 2
                mid_lon = (start_loc["lon"] + end_loc["lon"]) / 2

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
                await r.zadd(buffer_key, {_dump_packet(smooth_event): event_counter})
                event_counter += 1

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
                        "timestamp": end_time.isoformat().replace("+00:00", "Z"),
                        "offset_seconds": trip_duration_minutes * 60,
                        "trip_meter_km": float(trip_distance_km),
                        "odometer_km": float(end_odometer),
                        "location": {"lat": end_loc["lat"], "lon": end_loc["lon"]},
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
                await r.zadd(buffer_key, {_dump_packet(end_event): event_counter})
                event_counter += 1

                trips_created += 1

        return {
            "trucks": TRUCKS,
            "trips_per_truck": trips_per_truck,
            "trips_total": trips_created,
            "events_total": event_counter,
        }
    finally:
        await r.aclose()
