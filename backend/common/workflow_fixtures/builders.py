"""
Reusable TelemetryPacket-shaped dict builders for workflow fixtures.

All returned dicts are intended for ``TelemetryPacket.model_validate`` /
``json.dumps`` → Redis ``telemetry:{truck}:buffer``.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from common.samples.smoothness_batch import (
    build_smoothness_log_packet,
    smoothness_details_mild_variant,
)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat().replace("+00:00", "Z")


def new_ids(prefix: str) -> tuple[str, str]:
    """(event_id, device_event_id) with stable prefixes for debugging."""
    u = uuid.uuid4().hex[:12]
    return f"EVT-{prefix}-{u}", f"TEL-{prefix}-{u}"


def start_of_trip_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    at: datetime,
    odometer_km: float = 180_200.0,
    batch_id: str | None = None,
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    eid, did = new_ids("haccel")
    bid = f"BAT-haccel-{uuid.uuid4().hex[:12]}"
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
) -> dict[str, Any]:
    eid, did = new_ids("hbrake")
    bid = f"BAT-hbrake-{uuid.uuid4().hex[:12]}"
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
) -> dict[str, Any]:
    eid, did = new_ids("end")
    bid = f"BAT-end-{uuid.uuid4().hex[:12]}"
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
) -> dict[str, Any]:
    eid, did = new_ids("fb")
    bid = f"BAT-fb-{uuid.uuid4().hex[:12]}"
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
                "trip_rating": 4,
                "message": "Workflow fixture feedback after long trip.",
                "fatigue_self_report": "mild",
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
) -> dict[str, Any]:
    ts = anchor + timedelta(seconds=offset_seconds)
    eid, did = new_ids(f"sm{variant_seed}")
    bid = f"BAT-sm-{uuid.uuid4().hex[:10]}"
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
        details=smoothness_details_mild_variant(variant_seed),
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
