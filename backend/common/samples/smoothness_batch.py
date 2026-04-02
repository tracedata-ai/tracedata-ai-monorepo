"""
10-minute 1Hz smoothness batch (edge-computed statistics) — positive reinforcement layer.

Used by scoring as primary smoothness input. Matches device contract: nested
``details`` (speed, longitudinal, lateral, jerk, engine), optional
``incident_event_ids`` and ``raw_log_url`` (S3 compliance only).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


def reference_smoothness_batch_details() -> dict[str, Any]:
    """Static reference payload (documentation / golden sample)."""
    return {
        "sample_count": 600,
        "window_seconds": 600,
        "speed": {
            "mean_kmh": 72.3,
            "std_dev": 8.1,
            "max_kmh": 94.0,
            "variance": 65.6,
        },
        "longitudinal": {
            "mean_accel_g": 0.04,
            "std_dev": 0.12,
            "max_decel_g": -0.31,
            "harsh_brake_count": 0,
            "harsh_accel_count": 0,
        },
        "lateral": {
            "mean_lateral_g": 0.02,
            "max_lateral_g": 0.18,
            "harsh_corner_count": 0,
        },
        "jerk": {
            "mean": 0.008,
            "max": 0.041,
            "std_dev": 0.006,
        },
        "engine": {
            "mean_rpm": 1820,
            "max_rpm": 2340,
            "idle_seconds": 45,
            "idle_events": 1,
            "longest_idle_seconds": 38,
            "over_rev_count": 0,
            "over_rev_seconds": 0,
        },
        "incident_event_ids": ["DEV-HB-002", "DEV-SPD-006"],
        "raw_log_url": "s3://tracedata-sensors/T12345-batch-20260307-1010.bin",
    }


def build_smoothness_log_packet(
    *,
    trip_id: str,
    truck_id: str,
    driver_id: str,
    timestamp: datetime,
    offset_seconds: int,
    trip_meter_km: float,
    odometer_km: float,
    lat: float,
    lon: float,
    batch_id: str | None = None,
    event_id: str | None = None,
    device_event_id: str | None = None,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Full TelemetryPacket-shaped dict for Redis buffer / ingestion.

    Pass ``details`` to vary driving style; default is normal-driving reference.
    """
    ev_id = event_id or "EV-SMOOTH-REF"
    dev_id = device_event_id or "DEV-SMOOTH-REF"
    bid = batch_id or f"BATCH-{truck_id}-{timestamp.strftime('%Y%m%d-%H%M%S')}"
    body = details if details is not None else reference_smoothness_batch_details()

    return {
        "batch_id": bid,
        "ping_type": "batch",
        "source": "telematics_device",
        "is_emergency": False,
        "evidence": None,
        "event": {
            "event_id": ev_id,
            "device_event_id": dev_id,
            "trip_id": trip_id,
            "driver_id": driver_id,
            "truck_id": truck_id,
            "event_type": "smoothness_log",
            "category": "normal_operation",
            "priority": "low",
            "timestamp": (
                timestamp.isoformat().replace("+00:00", "Z")
                if timestamp.tzinfo
                else timestamp.isoformat()
            ),
            "offset_seconds": offset_seconds,
            "trip_meter_km": trip_meter_km,
            "odometer_km": odometer_km,
            "location": {"lat": lat, "lon": lon},
            "schema_version": "event_v1",
            "details": body,
        },
    }


def smoothness_details_mild_variant(seed: int = 0) -> dict[str, Any]:
    """Slightly different stats per trip for variety (still normal driving)."""
    base = reference_smoothness_batch_details()
    jitter = (seed % 7) * 0.001
    base = dict(base)
    base["jerk"] = {
        **base["jerk"],
        "mean": round(0.008 + jitter, 4),
        "max": round(0.041 + jitter * 2, 4),
        "std_dev": round(0.006 + jitter, 4),
    }
    base["speed"] = {**base["speed"], "std_dev": round(8.1 + (seed % 5) * 0.2, 1)}
    base["lateral"] = {
        **base["lateral"],
        "mean_lateral_g": round(0.02 + jitter, 3),
        "max_lateral_g": round(0.18 + jitter * 3, 3),
    }
    base["engine"] = {
        **base["engine"],
        "mean_rpm": 1820 + (seed % 4) * 15,
        "idle_seconds": 45 + (seed % 3) * 5,
    }
    return base
