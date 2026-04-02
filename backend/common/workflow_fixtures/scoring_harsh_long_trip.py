"""
~2-hour trip for scoring / orchestrator exercises:

  start_of_trip
  → 12 × smoothness_log (10-minute windows)
  → 1 × hard_accel
  → 3 × harsh_brake (interleaved with windows)
  → end_of_trip
  → driver_feedback (same trip_id)

Use: ``python scripts/play_workflow.py --fixture scoring_harsh_long_trip``
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.workflow_fixtures.builders import (
    driver_feedback_packet,
    end_of_trip_packet,
    hard_accel_packet,
    harsh_brake_packet,
    meters_for_offset,
    smoothness_at,
    start_of_trip_packet,
)

_END_OFFSET = 7380  # 123 min
_TOTAL_KM = 78.3
_BASE_OD = 180_200.0
_HARSH_TOTAL = 4  # 1 accel + 3 brakes

# (kind, offset_seconds, smooth_index_or_none)
_TIMELINE: list[tuple[str, int, int | None]] = [
    ("start", 0, None),
    ("smooth", 600, 1),
    ("smooth", 1200, 2),
    ("smooth", 1800, 3),
    ("accel", 2100, None),
    ("smooth", 2400, 4),
    ("smooth", 3000, 5),
    ("brake", 3480, None),
    ("smooth", 3600, 6),
    ("smooth", 4200, 7),
    ("brake", 4320, None),
    ("smooth", 4800, 8),
    ("smooth", 5400, 9),
    ("brake", 5760, None),
    ("smooth", 6000, 10),
    ("smooth", 6600, 11),
    ("smooth", 7200, 12),
    ("end", _END_OFFSET, None),
    ("feedback", _END_OFFSET + 420, None),
]


def build_events(
    *,
    trip_id: str | None = None,
    truck_id: str = "T12345",
    driver_id: str = "DRV-ANON-7829",
    anchor: datetime | None = None,
) -> list[dict[str, Any]]:
    tid = trip_id or f"TRP-WF-{uuid.uuid4().hex[:12]}"
    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    out: list[dict[str, Any]] = []

    for kind, off, idx in _TIMELINE:
        tm, od = meters_for_offset(off, _END_OFFSET, _TOTAL_KM, _BASE_OD)
        at = t0 + timedelta(seconds=off)

        if kind == "start":
            out.append(
                start_of_trip_packet(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    at=at,
                    odometer_km=_BASE_OD,
                )
            )
        elif kind == "smooth":
            assert idx is not None
            out.append(
                smoothness_at(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    anchor=t0,
                    offset_seconds=off,
                    trip_meter_km=tm,
                    odometer_km=od,
                    variant_seed=idx,
                )
            )
        elif kind == "accel":
            out.append(
                hard_accel_packet(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    at=at,
                    offset_seconds=off,
                    trip_meter_km=tm,
                    odometer_km=od,
                )
            )
        elif kind == "brake":
            out.append(
                harsh_brake_packet(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    at=at,
                    offset_seconds=off,
                    trip_meter_km=tm,
                    odometer_km=od,
                )
            )
        elif kind == "end":
            out.append(
                end_of_trip_packet(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    at=at,
                    offset_seconds=off,
                    trip_meter_km=_TOTAL_KM,
                    odometer_km=_BASE_OD + _TOTAL_KM,
                    harsh_events_total=_HARSH_TOTAL,
                )
            )
        elif kind == "feedback":
            out.append(
                driver_feedback_packet(
                    trip_id=tid,
                    truck_id=truck_id,
                    driver_id=driver_id,
                    at=at,
                    offset_seconds=off,
                )
            )

    return out
