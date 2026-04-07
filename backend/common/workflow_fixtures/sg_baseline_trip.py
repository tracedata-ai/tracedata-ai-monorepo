"""
Singapore baseline trip fixture:

  start_of_trip
  -> 3 x harsh_brake (HIGH)
  -> 12-18 x smoothness_log (10-minute windows; default 15)
  -> end_of_trip
  -> driver_feedback
"""

from __future__ import annotations

import random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.workflow_fixtures.builders import (
    driver_feedback_packet,
    end_of_trip_packet,
    hard_accel_packet,
    harsh_brake_packet,
    meters_for_offset,
    new_ids,
    smoothness_at,
    start_of_trip_packet,
)

# Common Singapore logistics corridors / hubs (lat, lon).
SG_HOTSPOTS: list[tuple[float, float]] = [
    (1.3010, 103.6200),  # Tuas
    (1.3250, 103.7090),  # Jurong
    (1.3470, 103.7210),  # Bukit Batok
    (1.4360, 103.7860),  # Woodlands
    (1.3760, 103.9550),  # Pasir Ris / East
    (1.3340, 103.9620),  # Changi Cargo
    (1.3120, 103.8590),  # CBD / Marina
    (1.2650, 103.8200),  # HarbourFront
]


def _sg_random_location(rng: random.Random) -> dict[str, float]:
    """Pick a Singapore hotspot and jitter slightly for realism."""
    base_lat, base_lon = rng.choice(SG_HOTSPOTS)
    # ~100-300m jitter
    lat = base_lat + rng.uniform(-0.002, 0.002)
    lon = base_lon + rng.uniform(-0.002, 0.002)
    return {"lat": round(lat, 6), "lon": round(lon, 6)}


def build_events(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    anchor: datetime | None = None,
    smooth_count: int = 15,
    random_seed: int | None = None,
) -> list[dict[str, Any]]:
    """
    Build one 2-3 hour equivalent trip timeline.
    smooth_count must be between 12 and 18 (inclusive).
    """
    if smooth_count < 12 or smooth_count > 18:
        raise ValueError("smooth_count must be between 12 and 18")

    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    rng = random.Random(random_seed)
    total_minutes = smooth_count * 10
    end_offset = (total_minutes * 60) + 180
    total_km = round((total_minutes / 60) * 30, 1)  # ~30 km/h average
    base_od = 180_000.0

    out: list[dict[str, Any]] = []

    # Start
    ev_id, dev_id = new_ids("start")
    out.append(
        start_of_trip_packet(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0,
            odometer_km=base_od,
            batch_id=f"BAT-start-{uuid.uuid4().hex[:10]}",
            event_id=ev_id,
            device_event_id=dev_id,
        )
    )

    # Smooth windows at 10-minute intervals
    for i in range(1, smooth_count + 1):
        off = i * 600
        tm, od = meters_for_offset(off, end_offset, total_km, base_od)
        ev_id, dev_id = new_ids(f"sm{i:02d}")
        out.append(
            smoothness_at(
                trip_id=trip_id,
                truck_id=truck_id,
                driver_id=driver_id,
                anchor=t0,
                offset_seconds=off,
                trip_meter_km=tm,
                odometer_km=od,
                variant_seed=i,
                batch_id=f"BAT-sm-{uuid.uuid4().hex[:10]}",
                event_id=ev_id,
                device_event_id=dev_id,
            )
        )

    # Exactly 3 harsh events spread across trip (mix of harsh_brake / hard_accel)
    harsh_offsets = [
        int(end_offset * 0.3),
        int(end_offset * 0.6),
        int(end_offset * 0.85),
    ]
    for idx, off in enumerate(harsh_offsets, start=1):
        tm, od = meters_for_offset(off, end_offset, total_km, base_od)
        # 2/3 brake, 1/3 accel on average.
        event_kind = "harsh_brake" if rng.random() < 0.67 else "hard_accel"
        ev_id, dev_id = new_ids(f"harsh{idx}")
        if event_kind == "harsh_brake":
            packet = harsh_brake_packet(
                trip_id=trip_id,
                truck_id=truck_id,
                driver_id=driver_id,
                at=t0 + timedelta(seconds=off),
                offset_seconds=off,
                trip_meter_km=tm,
                odometer_km=od,
                batch_id=f"BAT-hbrake-{uuid.uuid4().hex[:10]}",
                event_id=ev_id,
                device_event_id=dev_id,
            )
        else:
            packet = hard_accel_packet(
                trip_id=trip_id,
                truck_id=truck_id,
                driver_id=driver_id,
                at=t0 + timedelta(seconds=off),
                offset_seconds=off,
                trip_meter_km=tm,
                odometer_km=od,
                batch_id=f"BAT-haccel-{uuid.uuid4().hex[:10]}",
                event_id=ev_id,
                device_event_id=dev_id,
            )
        # Randomize harsh-event geolocation within Singapore for heatmap usage later.
        packet["event"]["location"] = _sg_random_location(rng)
        out.append(packet)

    # End + feedback
    ev_id, dev_id = new_ids("end")
    out.append(
        end_of_trip_packet(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0 + timedelta(seconds=end_offset),
            offset_seconds=end_offset,
            trip_meter_km=total_km,
            odometer_km=base_od + total_km,
            harsh_events_total=3,
            batch_id=f"BAT-end-{uuid.uuid4().hex[:10]}",
            event_id=ev_id,
            device_event_id=dev_id,
        )
    )

    ev_id, dev_id = new_ids("feedback")
    out.append(
        driver_feedback_packet(
            trip_id=trip_id,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0 + timedelta(seconds=end_offset + 420),
            offset_seconds=end_offset + 420,
            batch_id=f"BAT-fb-{uuid.uuid4().hex[:10]}",
            event_id=ev_id,
            device_event_id=dev_id,
        )
    )

    out.sort(key=lambda p: int(p["event"]["offset_seconds"]))
    return out
