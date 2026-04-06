"""
Short trip with a **collision** event so the Safety agent is routed and can run.

``scoring_harsh_long_trip`` does not include safety-only events (e.g. collision).

Use: ``python scripts/play_workflow.py --fixture safety_collision_trip``
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.workflow_fixtures.builders import (
    collision_packet,
    end_of_trip_packet,
    meters_for_offset,
    start_of_trip_packet,
)


def build_events(
    *,
    trip_id: str | None = None,
    truck_id: str = "T12345",
    driver_id: str = "DRV-ANON-SAFETY",
    anchor: datetime | None = None,
) -> list[dict[str, Any]]:
    tid = trip_id or f"TRP-SAFETY-{uuid.uuid4().hex[:12]}"
    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    base_od = 180_200.0
    total_km = 12.0
    end_s = 45 * 60
    col_s = 600

    tm_col, od_col = meters_for_offset(col_s, end_s, total_km, base_od)
    tm_end, od_end = meters_for_offset(end_s, end_s, total_km, base_od)

    return [
        start_of_trip_packet(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0,
            odometer_km=base_od,
        ),
        collision_packet(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0 + timedelta(seconds=col_s),
            offset_seconds=col_s,
            trip_meter_km=tm_col,
            odometer_km=od_col,
        ),
        end_of_trip_packet(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0 + timedelta(seconds=end_s),
            offset_seconds=end_s,
            trip_meter_km=tm_end,
            odometer_km=od_end,
            harsh_events_total=1,
        ),
    ]
