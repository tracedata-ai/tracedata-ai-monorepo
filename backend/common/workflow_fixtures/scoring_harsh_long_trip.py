"""
~2-hour trip for scoring / orchestrator exercises:

  start_of_trip
  → 12 × smoothness_log (10-minute windows)
  → 1 × hard_accel
  → 3 × harsh_brake (interleaved with windows)
  → end_of_trip
  → driver_feedback (same trip_id)

Correlation IDs follow ``docs/03-agents/0_input_data.md`` style (EVT-/TEL-/BAT- + UUID-like segments);
default ``trip_id`` matches the doc single-trip fixture.

Use:

  ``python scripts/play_workflow.py --fixture scoring_harsh_long_trip``
  ``python scripts/play_workflow.py --fixture scoring_harsh_long_trip --segments start,end``
  ``python scripts/play_workflow.py --fixture scoring_harsh_long_trip --start-only``  # same as ``--segments start``
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from common.workflow_fixtures.builders import (
    doc_style_batch,
    doc_style_evt_tel,
    driver_feedback_packet,
    end_of_trip_packet,
    hard_accel_packet,
    harsh_brake_packet,
    meters_for_offset,
    smoothness_at,
    start_of_trip_packet,
)

# Same canonical trip as ``docs/03-agents/0_input_data.md`` (override via play_workflow --trip-id).
CANONICAL_TRIP_ID = "TRP-2026-a1b2c3d4-e5f6-47g8-h9i0-j1k2l3m4n5o6"

TRIP_SEGMENTS_ALL: frozenset[str] = frozenset(
    {"start", "smooth", "harsh", "end", "feedback"}
)

_KIND_TO_SEGMENT: dict[str, str] = {
    "start": "start",
    "smooth": "smooth",
    "accel": "harsh",
    "brake": "harsh",
    "end": "end",
    "feedback": "feedback",
}

_END_OFFSET = 7380  # 123 min
_TOTAL_KM = 78.3
_BASE_OD = 180_200.0


def parse_trip_segments(s: str) -> frozenset[str]:
    parts = [p.strip().lower() for p in s.split(",") if p.strip()]
    if not parts:
        raise ValueError("segments list is empty")
    unknown = set(parts) - TRIP_SEGMENTS_ALL
    if unknown:
        raise ValueError(
            f"unknown segment(s): {', '.join(sorted(unknown))}; "
            f"expected one or more of: {', '.join(sorted(TRIP_SEGMENTS_ALL))}"
        )
    return frozenset(parts)


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
    segments: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Build the timeline in order. ``segments`` selects which groups to emit (default: all).
    Correlation ids are numbered 0..N-1 over emitted packets only.
    ``end_of_trip.harsh_events_total`` matches the number of harsh packets actually emitted.
    """
    tid = trip_id or CANONICAL_TRIP_ID
    t0 = anchor or datetime.now(UTC).replace(microsecond=0)
    active = TRIP_SEGMENTS_ALL if segments is None else segments
    if not active:
        raise ValueError("segments must be non-empty")
    extra = active - TRIP_SEGMENTS_ALL
    if extra:
        raise ValueError(f"invalid segment(s): {', '.join(sorted(extra))}")

    out: list[dict[str, Any]] = []
    harsh_emitted = 0
    emit_seq = 0

    for kind, off, idx in _TIMELINE:
        seg = _KIND_TO_SEGMENT[kind]
        if seg not in active:
            continue

        ev_id, dev_id = doc_style_evt_tel(emit_seq)
        bat = doc_style_batch(emit_seq)
        emit_seq += 1
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
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
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
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
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
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
                )
            )
            harsh_emitted += 1
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
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
                )
            )
            harsh_emitted += 1
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
                    harsh_events_total=harsh_emitted,
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
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
                    batch_id=bat,
                    event_id=ev_id,
                    device_event_id=dev_id,
                )
            )

    return out
