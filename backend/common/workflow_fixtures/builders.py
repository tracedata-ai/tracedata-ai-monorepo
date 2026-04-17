"""
Reusable TelemetryPacket-shaped dict builders for workflow fixtures.

All returned dicts are intended for ``TelemetryPacket.model_validate`` /
``json.dumps`` → Redis ``telemetry:{truck}:buffer``.
"""

from __future__ import annotations

import random as _random
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    smoothness_details_mild_variant,
)
from common.workflow_fixtures.mock_driver_feedback import (
    FEEDBACK_POOL as _FEEDBACK_POOL,
)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat().replace("+00:00", "Z")


def new_ids(prefix: str) -> tuple[str, str]:
    """(event_id, device_event_id) with stable prefixes for debugging."""
    u = uuid.uuid4().hex[:12]
    return f"EVT-{prefix}-{u}", f"TEL-{prefix}-{u}"


def doc_style_evt_tel(seq: int) -> tuple[str, str]:
    """
    IDs in the style of ``docs/03-agents/0_input_data.md`` (8-4-4-4-12 after prefix).

    ``seq`` 0 matches the start-of-trip example:
    ``EVT-6ba7b810-9dad-11d1-80b4-00c04fd430c8`` /
    ``TEL-6ba7b811-9dad-11d1-80b4-00c04fd430c8``.
    """
    if seq < 0:
        raise ValueError("seq must be non-negative")
    first_evt = 0x6BA7B810 + seq
    first_tel = 0x6BA7B811 + seq
    mid = "9dad-11d1-80b4"
    suffix = 0x00C04FD430C8 + seq
    last12 = f"{suffix:012x}"
    return (
        f"EVT-{first_evt:08x}-{mid}-{last12}",
        f"TEL-{first_tel:08x}-{mid}-{last12}",
    )


def doc_style_batch(seq: int) -> str:
    """Batch id style aligned with the same doc (BAT- + UUID-like tail)."""
    if seq < 0:
        raise ValueError("seq must be non-negative")
    hi = 0x6BA7B900 + seq
    mid = "9dad-11d1-80b4"
    tail = f"{(0x00C04FD430C8 + seq):012x}"
    return f"BAT-{hi:08x}-{mid}-{tail}"


def start_of_trip_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    odometer_km: float = 180_200.0,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("start")
    bid = batch_id or f"BAT-start-{uuid.uuid4().hex[:12]}"
    return {
        "batch_id": bid,
        "ping_type": "start_of_trip",
        "source": "driver_app",
        "is_emergency": False,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "start_of_trip",
            "category": "trip_lifecycle",
            "priority": "low",
            "timestamp": _iso(at),
            "offset_seconds": 0,
            "trip_meter_km": 0.0,
            "odometer_km": odometer_km,
            "location": {"lat": 1.3456, "lon": 103.8301},
            "schema_version": "event_v1",
            "details": {
                "odometer_km": odometer_km,
                "fuel_level_litres": 45,
                "vehicle_status": "ready",
                "driver_confirmation": True,
                "intended_destination": "Port (workflow fixture)",
                "estimated_distance_km": 78,
            },
        },
    }


def hard_accel_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("haccel")
    bid = batch_id or f"BAT-haccel-{uuid.uuid4().hex[:12]}"
    return {
        "batch_id": bid,
        "ping_type": "high_speed",
        "source": "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "hard_accel",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": _iso(at),
            "offset_seconds": offset_seconds,
            "trip_meter_km": trip_meter_km,
            "odometer_km": odometer_km,
            "location": {"lat": 1.31, "lon": 103.86},
            "schema_version": "event_v1",
            "details": {
                "g_force_x": 0.82,
                "speed_kmh": 42,
                "duration_seconds": 3,
                "confidence": 0.91,
            },
        },
        "evidence": {
            "video_url": f"s3://tracedata-clips/{bid}.mp4",
            "video_duration_seconds": 30,
            "capture_offset_seconds": -15,
        },
    }


def harsh_brake_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("hbrake")
    bid = batch_id or f"BAT-hbrake-{uuid.uuid4().hex[:12]}"
    return {
        "batch_id": bid,
        "ping_type": "high_speed",
        "source": "telematics_device",
        "is_emergency": False,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "harsh_brake",
            "category": "harsh_events",
            "priority": "high",
            "timestamp": _iso(at),
            "offset_seconds": offset_seconds,
            "trip_meter_km": trip_meter_km,
            "odometer_km": odometer_km,
            "location": {"lat": 1.3112, "lon": 103.861},
            "schema_version": "event_v1",
            "details": {
                "g_force_x": -0.82,
                "speed_kmh": 42,
                "duration_seconds": 3,
                "confidence": 0.91,
            },
        },
        "evidence": {
            "video_url": f"s3://tracedata-clips/{bid}.mp4",
            "video_duration_seconds": 30,
            "capture_offset_seconds": -15,
        },
    }


def collision_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("collision")
    bid = batch_id or f"BAT-collision-{uuid.uuid4().hex[:12]}"
    return {
        "batch_id": bid,
        "ping_type": "emergency",
        "source": "telematics_device",
        "is_emergency": True,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "collision",
            "category": "critical",
            "priority": "critical",
            "severity": "critical",
            "timestamp": _iso(at),
            "offset_seconds": offset_seconds,
            "trip_meter_km": trip_meter_km,
            "odometer_km": odometer_km,
            "location": {"lat": 1.31, "lon": 103.86},
            "schema_version": "event_v1",
            "details": {
                "impact_force_g": 2.4,
                "speed_kmh": 35,
                "airbags_deployed": False,
            },
        },
        "evidence": {
            "video_url": f"s3://tracedata-clips/{bid}.mp4",
            "video_duration_seconds": 60,
            "capture_offset_seconds": -20,
        },
    }


def end_of_trip_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    harsh_events_total: int = 0,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("end")
    bid = batch_id or f"BAT-end-{uuid.uuid4().hex[:12]}"
    return {
        "batch_id": bid,
        "ping_type": "end_of_trip",
        "source": "driver_app",
        "is_emergency": False,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "end_of_trip",
            "category": "trip_lifecycle",
            "priority": "low",
            "timestamp": _iso(at),
            "offset_seconds": offset_seconds,
            "trip_meter_km": trip_meter_km,
            "odometer_km": odometer_km,
            "location": {"lat": 1.29, "lon": 103.85},
            "schema_version": "event_v1",
            "details": {
                "duration_minutes": max(1, offset_seconds // 60),
                "distance_km": trip_meter_km,
                "harsh_events_total": harsh_events_total,
                "speeding_events": 0,
                "safe_operation_checkpoints": 28,
                "total_checkpoints": 28,
                "safety_percentage": 92.9,
                "fuel_consumed_litres": 9.8,
                "avg_speed_kmh": 28.5,
                "max_speed_kmh": 94.0,
            },
        },
    }


def driver_feedback_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    offset_seconds: int,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
    style: str | None = None,
) -> dict[str, Any]:
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids("fb")
    bid = batch_id or f"BAT-fb-{uuid.uuid4().hex[:12]}"
    if style in {"excellent", "good"}:
        pool = [e for e in _FEEDBACK_POOL if e[1] >= 4]
    elif style == "average":
        pool = [e for e in _FEEDBACK_POOL if e[1] == 3]
    elif style in {"poor", "aggressive"}:
        pool = [e for e in _FEEDBACK_POOL if e[1] <= 2]
    else:
        pool = list(_FEEDBACK_POOL)
    message, rating, fatigue = _random.choice(pool or list(_FEEDBACK_POOL))
    return {
        "batch_id": bid,
        "ping_type": "medium_speed",
        "source": "driver_app",
        "is_emergency": False,
        "event": {
            "event_id": eid,
            "device_event_id": did,
            "trip_id": trip_id,
            "truck_id": truck_id,
            "driver_id": driver_id,
            "batch_id": bid,
            "event_type": "driver_feedback",
            "category": "driver_feedback",
            "priority": "medium",
            "timestamp": _iso(at),
            "offset_seconds": offset_seconds,
            "trip_meter_km": None,
            "odometer_km": None,
            "location": None,
            "schema_version": "event_v1",
            "details": {
                "trip_rating": rating,
                "message": message,
                "fatigue_self_report": fatigue,
            },
        },
    }


def smoothness_at(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    anchor: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    variant_seed: int,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ts = anchor + timedelta(seconds=offset_seconds)
    if event_id and device_event_id:
        eid, did = event_id, device_event_id
    else:
        eid, did = new_ids(f"sm{variant_seed}")
    bid = batch_id or f"BAT-sm-{uuid.uuid4().hex[:10]}"
    return build_smoothness_log_packet(
        trip_id=trip_id,
        truck_id=truck_id,
        driver_id=driver_id,
        timestamp=ts,
        offset_seconds=offset_seconds,
        trip_meter_km=trip_meter_km,
        odometer_km=odometer_km,
        lat=1.347 + variant_seed * 0.0003,
        lon=103.834 + variant_seed * 0.0002,
        batch_id=bid,
        event_id=eid,
        device_event_id=did,
        details=(
            details
            if details is not None
            else smoothness_details_mild_variant(variant_seed)
        ),
    )


def meters_for_offset(
    offset_seconds: int, end_offset: int, total_km: float, base_odometer: float
) -> tuple[float, float]:
    """Linear interpolate trip_meter and odometer for narrative consistency."""
    if end_offset <= 0:
        return 0.0, base_odometer
    frac = min(1.0, max(0.0, offset_seconds / end_offset))
    trip_m = round(total_km * frac, 1)
    return trip_m, round(base_odometer + trip_m, 1)
