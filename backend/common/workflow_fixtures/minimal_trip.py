"""
Minimal pipeline smoke trip: start → one smoothness batch → end.

Use: ``python scripts/play_workflow.py --fixture minimal_trip``
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.workflow_fixtures.builders import (
    end_of_trip_packet,
    meters_for_offset,
    smoothness_at,
    start_of_trip_packet,
)


def build_events(
    *,
    trip_id: str | None = None,
    truck_id: str = "TK001",
    driver_id: str = "DRV-ANON-7829",
    anchor: datetime | None = None,
) -> list[dict[str, Any]]:
    tid = trip_id or f"TRP-WF-{uuid.uuid4().hex[:12]}"
    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    base_od = 180_200.0
    total_km = 15.0
    end_s = 30 * 60

    tm_mid, od_mid = meters_for_offset(900, end_s, total_km, base_od)
    tm_end, od_end = meters_for_offset(end_s, end_s, total_km, base_od)

    return [
        start_of_trip_packet(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0,
            odometer_km=base_od,
        ),
        smoothness_at(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            anchor=t0,
            offset_seconds=900,
            trip_meter_km=tm_mid,
            odometer_km=od_mid,
            variant_seed=1,
        ),
        end_of_trip_packet(
            trip_id=tid,
            truck_id=truck_id,
            driver_id=driver_id,
            at=t0 + timedelta(seconds=end_s),
            offset_seconds=end_s,
            trip_meter_km=tm_end,
            odometer_km=od_end,
            harsh_events_total=0,
        ),
    ]
