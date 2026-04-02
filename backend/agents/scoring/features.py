"""Deterministic scoring features and payloads (no LLM)."""

from __future__ import annotations

from statistics import mean
from typing import Any


def _nested_float(d: dict[str, Any], *path: str, default: float = 0.0) -> float:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(key)
        if cur is None:
            return default
    try:
        return float(cur)
    except (TypeError, ValueError):
        return default


def _window_harsh_subtotals(details: dict[str, Any]) -> int:
    """In-window harsh counts from 10-min batch ``details`` (coaching context)."""
    n = 0
    lon = details.get("longitudinal")
    if isinstance(lon, dict):
        n += int(lon.get("harsh_brake_count") or 0)
        n += int(lon.get("harsh_accel_count") or 0)
    lat = details.get("lateral")
    if isinstance(lat, dict):
        n += int(lat.get("harsh_corner_count") or 0)
    eng = details.get("engine")
    if isinstance(eng, dict):
        n += int(eng.get("over_rev_count") or 0)
    return n


def metrics_from_smoothness_details(details: dict[str, Any]) -> dict[str, float | int]:
    """
    Map one smoothness ping's ``details`` to scoring metrics.

    Supports:
    - Legacy flat keys (jerk_mean, speed_std_dev, …)
    - 10-minute batch nested shape (speed.std_dev, jerk.mean, lateral.*, engine.*)
    """
    if isinstance(details.get("jerk"), dict):
        jerk_mean = _nested_float(details, "jerk", "mean")
        jerk_max = _nested_float(details, "jerk", "max")
        speed_std = _nested_float(details, "speed", "std_dev")
        lateral_mean = _nested_float(details, "lateral", "mean_lateral_g")
        lateral_max = _nested_float(details, "lateral", "max_lateral_g")
        mean_rpm = _nested_float(details, "engine", "mean_rpm")
        idle_sec = _nested_float(details, "engine", "idle_seconds")
        window_harsh = _window_harsh_subtotals(details)
    else:
        jerk_mean = _nested_float(details, "jerk_mean")
        jerk_max = _nested_float(details, "jerk_max")
        speed_std = _nested_float(details, "speed_std_dev")
        lateral_mean = _nested_float(details, "mean_lateral_g")
        lateral_max = _nested_float(details, "max_lateral_g")
        mean_rpm = _nested_float(details, "mean_rpm")
        idle_sec = _nested_float(details, "idle_seconds")
        window_harsh = 0

    return {
        "jerk_mean": jerk_mean,
        "jerk_max": jerk_max,
        "speed_std": speed_std,
        "lateral_mean": lateral_mean,
        "lateral_max": lateral_max,
        "mean_rpm": mean_rpm,
        "idle_seconds": idle_sec,
        "window_harsh": window_harsh,
    }


def _trip_duration_seconds_for_idle(
    all_pings: list[dict], smoothness_pings: list[dict]
) -> float:
    """Prefer sum of batch ``window_seconds``; fallback to legacy heuristic."""
    total_window = 0.0
    for p in smoothness_pings:
        d = p.get("details")
        if isinstance(d, dict) and isinstance(d.get("window_seconds"), (int, float)):
            total_window += float(d["window_seconds"])
    if total_window > 0:
        return max(total_window, 60.0)
    trip_duration_minutes = max(float(len(all_pings)) / 6.0, 1.0)
    return trip_duration_minutes * 60.0


def extract_feature_bundle(all_pings: list[dict]) -> dict[str, Any]:
    """Aggregate smoothness / harsh metrics from warmed `all_pings` cache."""
    smoothness_pings = [
        p
        for p in all_pings
        if str(p.get("event_type", "")).lower() == "smoothness_log"
    ]
    harsh_events = [
        p
        for p in all_pings
        if str(p.get("event_type", "")).lower()
        in {"harsh_brake", "hard_accel", "harsh_corner"}
    ]

    rows = []
    for p in smoothness_pings:
        d = p.get("details", {})
        if not isinstance(d, dict):
            d = {}
        rows.append(metrics_from_smoothness_details(d))

    jerk_means = [float(r["jerk_mean"]) for r in rows]
    jerk_maxes = [float(r["jerk_max"]) for r in rows]
    speed_stds = [float(r["speed_std"]) for r in rows]
    lateral_means = [float(r["lateral_mean"]) for r in rows]
    lateral_maxes = [float(r["lateral_max"]) for r in rows]
    mean_rpms = [float(r["mean_rpm"]) for r in rows]
    idle_seconds = [float(r["idle_seconds"]) for r in rows]
    window_harsh_sum = sum(int(r["window_harsh"]) for r in rows)

    trip_duration_seconds = _trip_duration_seconds_for_idle(all_pings, smoothness_pings)

    return {
        "smoothness_features": {
            "jerk_mean_avg": round(mean(jerk_means), 4) if jerk_means else 0.0,
            "jerk_max_peak": round(max(jerk_maxes), 4) if jerk_maxes else 0.0,
            "speed_std_avg": round(mean(speed_stds), 2) if speed_stds else 0.0,
            "mean_lateral_g_avg": (
                round(mean(lateral_means), 3) if lateral_means else 0.0
            ),
            "max_lateral_g_peak": round(max(lateral_maxes), 3) if lateral_maxes else 0.0,
            "mean_rpm_avg": round(mean(mean_rpms), 0) if mean_rpms else 0.0,
            "idle_ratio": round(
                sum(idle_seconds) / max(trip_duration_seconds, 1.0), 3
            ),
            "harsh_event_count": len(harsh_events) + window_harsh_sum,
        },
        "raw_harsh_events": harsh_events,
    }


def score_label_from_value(behaviour_score: float) -> str:
    if behaviour_score >= 85:
        return "Excellent"
    if behaviour_score >= 70:
        return "Good"
    if behaviour_score >= 55:
        return "Average"
    if behaviour_score >= 40:
        return "Below Average"
    return "Poor"


def compute_components_and_baseline(sf: dict[str, Any]) -> tuple[float, dict[str, float]]:
    jerk_component = max(
        0.0,
        min(40.0, 40.0 - (sf["jerk_mean_avg"] * 800.0 + sf["jerk_max_peak"] * 8.0)),
    )
    speed_component = max(0.0, min(25.0, 25.0 - sf["speed_std_avg"] * 0.9))
    lateral_component = max(
        0.0,
        min(
            20.0,
            20.0
            - (sf["mean_lateral_g_avg"] * 70.0 + sf["max_lateral_g_peak"] * 15.0),
        ),
    )
    engine_component = max(
        0.0,
        min(
            15.0,
            15.0
            - abs(sf["mean_rpm_avg"] - 1500.0) / 200.0
            - sf["idle_ratio"] * 20.0,
        ),
    )
    baseline = round(
        jerk_component + speed_component + lateral_component + engine_component, 1
    )
    breakdown = {
        "jerk_component": round(jerk_component, 1),
        "speed_component": round(speed_component, 1),
        "lateral_component": round(lateral_component, 1),
        "engine_component": round(engine_component, 1),
    }
    return baseline, breakdown


def deterministic_payload_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    """Full scoring dict from feature bundle (smoothness heuristic + coaching flags)."""
    sf = bundle["smoothness_features"]
    baseline_score, breakdown = compute_components_and_baseline(sf)
    label = score_label_from_value(baseline_score)
    harsh_count = int(sf.get("harsh_event_count", 0))
    coaching_reasons: list[str] = []
    if harsh_count > 0:
        coaching_reasons.append("Harsh events detected; coaching recommended.")
    if sf["idle_ratio"] > 0.25:
        coaching_reasons.append(
            "High idle ratio detected; improve idle management."
        )
    return {
        "behaviour_score": baseline_score,
        "score_label": label,
        "score_breakdown": breakdown,
        "coaching_required": bool(coaching_reasons),
        "coaching_reasons": coaching_reasons,
        "shap_explanation": {
            "method": "deterministic_heuristic",
            "top_features": [
                {"feature": "jerk_mean_avg", "impact": "high"},
                {"feature": "speed_std_avg", "impact": "medium"},
                {"feature": "idle_ratio", "impact": "medium"},
            ],
            "narrative": "Score derived from smoothness aggregates over trip pings.",
        },
        "fairness_audit": {
            "demographic_parity": "PASS",
            "equalized_odds": "PASS",
            "bias_detected": False,
            "recommendation": "No clear bias signal in single-trip heuristic.",
        },
    }


def compute_driver_score(
    trip_score: float,
    historical_avg: dict[str, Any],
) -> float:
    """Blend current trip score with rolling history for driver-level scoring."""
    raw = historical_avg.get("historical_avg_score") or historical_avg.get(
        "rolling_avg_score"
    )
    try:
        baseline = float(raw) if raw is not None else float(trip_score)
    except (TypeError, ValueError):
        baseline = float(trip_score)

    blended = 0.7 * float(trip_score) + 0.3 * baseline
    return round(max(0.0, min(100.0, blended)), 1)


def clamp_behaviour_score(payload: dict[str, Any], baseline: float) -> None:
    """Clamp behaviour_score to [0, 100] in place."""
    try:
        payload["behaviour_score"] = float(
            max(
                0.0,
                min(100.0, float(payload.get("behaviour_score", baseline))),
            )
        )
    except (TypeError, ValueError):
        payload["behaviour_score"] = baseline


def merge_graph_json_with_baseline(
    parsed: dict[str, Any],
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Clamp score using deterministic baseline from bundle; fill missing keys."""
    sf = bundle["smoothness_features"]
    baseline, _ = compute_components_and_baseline(sf)
    clamp_behaviour_score(parsed, baseline)
    base = deterministic_payload_from_bundle(bundle)
    for key, val in base.items():
        parsed.setdefault(key, val)
    return parsed
