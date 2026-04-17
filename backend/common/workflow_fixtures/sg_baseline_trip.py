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

from common.samples.smoothness_batch import (
    DRIVING_STYLES,
    STYLE_WEIGHTS,
    smoothness_details_for_style,
)
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
from common.workflow_fixtures.sg_harsh_locations import pick_sg_harsh_location


def build_events(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    anchor: datetime | None = None,
    smooth_count: int = 15,
    harsh_count: int = 3,
    random_seed: int | None = None,
    style: str | None = None,
) -> list[dict[str, Any]]:
    """
    Build one complete trip timeline.

    Args:
        smooth_count: Number of 10-minute smoothness windows (6–24).
        harsh_count:  Number of harsh driving events (2–6).
        style: Driving style archetype override. If None, chosen randomly from
               DRIVING_STYLES with STYLE_WEIGHTS. Pass explicitly to guarantee
               a specific tier appears in the batch.
    """
    if smooth_count < 6 or smooth_count > 24:
        raise ValueError("smooth_count must be between 6 and 24")
    if harsh_count < 2 or harsh_count > 6:
        raise ValueError("harsh_count must be between 2 and 6")

    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    rng = random.Random(random_seed)
    if style is None:
        style = rng.choices(DRIVING_STYLES, weights=STYLE_WEIGHTS, k=1)[0]
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

    # Smooth windows at 10-minute intervals — each window gets style-specific details
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
                details=smoothness_details_for_style(style, rng),
            )
        )

    # 2–6 harsh events spread evenly across the middle 70% of the trip
    # (avoid clustering at start/end where traffic is lighter)
    spread_start = 0.15
    spread_end = 0.85
    if harsh_count == 1:
        fracs = [0.5]
    else:
        step = (spread_end - spread_start) / (harsh_count - 1)
        fracs = [spread_start + i * step for i in range(harsh_count)]
    harsh_offsets = [int(end_offset * f) for f in fracs]

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
        lat, lon, place_name = pick_sg_harsh_location(rng)
        packet["event"]["location"] = {"lat": lat, "lon": lon, "place_name": place_name}
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
            harsh_events_total=harsh_count,
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
            style=style,
        )
    )

    out.sort(key=lambda p: int(p["event"]["offset_seconds"]))
    return out
