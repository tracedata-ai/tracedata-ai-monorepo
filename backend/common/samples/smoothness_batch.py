"""
10-minute 1Hz smoothness batch (edge-computed statistics) — positive reinforcement layer.

Used by scoring as primary smoothness input. Matches device contract: nested
``details`` (speed, longitudinal, lateral, jerk, engine), optional
``incident_event_ids`` and ``raw_log_url`` (S3 compliance only).
"""

from __future__ import annotations

import random as _random
from datetime import datetime
from typing import Any

# Driving style archetypes — assign one per trip so the dashboard shows real variance.
# Weights give a realistic fleet distribution (most drivers are decent, few excellent/aggressive).
DRIVING_STYLES: list[str] = ["excellent", "good", "average", "poor", "aggressive"]
STYLE_WEIGHTS: list[float] = [0.12, 0.28, 0.32, 0.18, 0.10]


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


def smoothness_details_for_style(
    style: str,
    rng: _random.Random,
) -> dict[str, Any]:
    """
    Generate one smoothness_log details window for a specific driving style archetype.

    Produces genuine variance across the full scoring range so dashboards show
    meaningful score differences rather than a uniform cluster.

    ML model feature mapping (loader._extract_features):
        accel_fluidity      = clip(1 - jerk_mean * 10, 0, 1)
        driving_consistency = clip(1 - speed_std / 30, 0, 1)
        comfort_zone_pct    = clip(1 - lat_mean/0.3 - jerk_max/5, 0, 1)

    Approximate ML output ranges (XGBoost, [0→1] scaled ×100):
        excellent  →  70–82   (near-perfect inputs push all three features ≥0.95)
        good       →  52–68
        average    →  32–48
        poor       →  16–30
        aggressive →   4–18
    """
    v = rng.uniform
    i = rng.randint

    if style == "excellent":
        # Near-perfect: all three ML features ≥ 0.95 so the model scores high.
        jerk_mean = v(0.0008, 0.002)  # accel_fluidity ≥ 0.98
        jerk_max = v(0.005, 0.018)  # comfort driver: jerk_max/5 ≤ 0.004
        jerk_std = v(0.001, 0.002)
        spd_mean = v(55.0, 70.0)
        spd_std = v(0.5, 2.0)  # consistency ≥ 0.93
        spd_max = v(65.0, 80.0)
        lat_mean = v(0.002, 0.008)  # comfort driver: lat_mean/0.3 ≤ 0.027
        lat_max = v(0.015, 0.045)
        h_brake = 0
        h_accel = 0
        h_corner = 0
        over_rev = 0
        rpm = i(1450, 1650)
        idle_sec = i(15, 40)
    elif style == "good":
        jerk_mean = v(0.006, 0.016)
        jerk_max = v(0.035, 0.10)
        jerk_std = v(0.004, 0.009)
        spd_mean = v(50.0, 72.0)
        spd_std = v(5.0, 12.0)
        spd_max = v(72.0, 94.0)
        lat_mean = v(0.018, 0.055)
        lat_max = v(0.09, 0.22)
        h_brake = 0
        h_accel = 0
        h_corner = i(0, 1)
        over_rev = 0
        rpm = i(1600, 1950)
        idle_sec = i(35, 75)
    elif style == "average":
        jerk_mean = v(0.014, 0.030)
        jerk_max = v(0.08, 0.24)
        jerk_std = v(0.008, 0.015)
        spd_mean = v(45.0, 68.0)
        spd_std = v(10.0, 18.0)
        spd_max = v(76.0, 98.0)
        lat_mean = v(0.045, 0.11)
        lat_max = v(0.14, 0.34)
        h_brake = i(0, 1)
        h_accel = i(0, 1)
        h_corner = i(0, 2)
        over_rev = i(0, 1)
        rpm = i(1700, 2100)
        idle_sec = i(55, 110)
    elif style == "poor":
        jerk_mean = v(0.028, 0.050)
        jerk_max = v(0.18, 0.45)
        jerk_std = v(0.014, 0.024)
        spd_mean = v(40.0, 65.0)
        spd_std = v(15.0, 22.0)
        spd_max = v(80.0, 105.0)
        lat_mean = v(0.10, 0.21)
        lat_max = v(0.26, 0.55)
        h_brake = i(1, 3)
        h_accel = i(0, 2)
        h_corner = i(1, 3)
        over_rev = i(0, 3)
        rpm = i(1900, 2450)
        idle_sec = i(85, 160)
    else:  # aggressive
        jerk_mean = v(0.050, 0.092)
        jerk_max = v(0.35, 0.90)
        jerk_std = v(0.022, 0.035)
        spd_mean = v(60.0, 88.0)
        spd_std = v(18.0, 28.0)
        spd_max = v(90.0, 118.0)
        lat_mean = v(0.18, 0.30)
        lat_max = v(0.40, 0.85)
        h_brake = i(2, 4)
        h_accel = i(2, 4)
        h_corner = i(2, 5)
        over_rev = i(1, 4)
        rpm = i(2200, 2900)
        idle_sec = i(20, 65)

    return {
        "sample_count": 600,
        "window_seconds": 600,
        "speed": {
            "mean_kmh": round(spd_mean, 1),
            "std_dev": round(spd_std, 2),
            "max_kmh": round(spd_max, 1),
            "variance": round(spd_std**2, 2),
        },
        "longitudinal": {
            "mean_accel_g": round(jerk_mean * 2.5, 4),
            "std_dev": round(jerk_std * 3.0, 4),
            "max_decel_g": round(-jerk_max * 4.0, 3),
            "harsh_brake_count": h_brake,
            "harsh_accel_count": h_accel,
        },
        "lateral": {
            "mean_lateral_g": round(lat_mean, 4),
            "max_lateral_g": round(lat_max, 3),
            "harsh_corner_count": h_corner,
        },
        "jerk": {
            "mean": round(jerk_mean, 4),
            "max": round(jerk_max, 3),
            "std_dev": round(jerk_std, 4),
        },
        "engine": {
            "mean_rpm": rpm,
            "max_rpm": int(rpm * 1.3),
            "idle_seconds": idle_sec,
            "idle_events": max(1, idle_sec // 30),
            "longest_idle_seconds": int(idle_sec * 0.65),
            "over_rev_count": over_rev,
            "over_rev_seconds": over_rev * i(2, 8) if over_rev else 0,
        },
        "incident_event_ids": [],
        "raw_log_url": None,
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
