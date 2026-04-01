"""
Scoring Agent Tools (backend copy).

This module mirrors the prototype tools contract so scoring logic can be reused
from the real backend agent package.
"""

import json
from typing import Any

from langchain_core.tools import tool

# Runtime service registry for tool calls executed by LLM agents.
_RUNTIME_SERVICES: dict[str, Any] = {
    "xai_engine": None,
    "fairness_auditor": None,
}


def configure_scoring_tool_runtime(
    *, xai_engine: Any = None, fairness_auditor: Any = None
) -> None:
    """Inject runtime services used by tools during LLM-driven execution."""
    _RUNTIME_SERVICES["xai_engine"] = xai_engine
    _RUNTIME_SERVICES["fairness_auditor"] = fairness_auditor


@tool
def get_trip_context(trip_id: str, redis_client: Any = None) -> str:
    """Get trip context from Redis; fallback to demo payload."""
    if redis_client is not None:
        try:
            value = redis_client.get(f"trip:{trip_id}:context")
            if value:
                if isinstance(value, bytes):
                    return value.decode("utf-8")
                return str(value)
        except Exception:
            pass

    return json.dumps(
        {
            "trip_id": trip_id,
            "driver_id": "driver_id_placeholder",
            "truck_id": "truck_id_placeholder",
            "distance_km": 120.5,
            "duration_minutes": 185.0,
            "driver_age": 35,
            "experience_level": "medium",
            "historical_avg_score": 71.2,
            "peer_group_avg": 69.8,
        }
    )


@tool
def get_smoothness_logs(trip_id: str, redis_client: Any = None) -> str:
    """Get smoothness windows from Redis; fallback to demo window."""
    if redis_client is not None:
        try:
            values = redis_client.lrange(f"trip:{trip_id}:smoothness_logs", 0, -1)
            if values:
                windows = []
                for idx, item in enumerate(values):
                    raw = item.decode("utf-8") if isinstance(item, bytes) else str(item)
                    window = json.loads(raw)
                    if "window_index" not in window:
                        window["window_index"] = idx
                    windows.append(window)
                return json.dumps({"window_count": len(windows), "windows": windows})
        except Exception:
            pass

    return json.dumps(
        {
            "window_count": 1,
            "windows": [
                {
                    "window_index": 0,
                    "trip_meter_km": 22.4,
                    "jerk_mean": 0.015,
                    "jerk_max": 1.92,
                    "speed_std_dev": 11.8,
                    "mean_lateral_g": 0.032,
                    "max_lateral_g": 0.15,
                    "mean_rpm": 1480,
                    "idle_seconds": 35,
                }
            ],
        }
    )


@tool
def get_harsh_events(trip_id: str, redis_client: Any = None) -> str:
    """Get harsh events from Redis; fallback to demo event list."""
    if redis_client is not None:
        try:
            values = redis_client.lrange(f"trip:{trip_id}:harsh_events", 0, -1)
            if values:
                events = []
                for item in values:
                    raw = item.decode("utf-8") if isinstance(item, bytes) else str(item)
                    events.append(json.loads(raw))
                return json.dumps({"event_count": len(events), "events": events})
        except Exception:
            pass

    demo_events = [
        {
            "event_id": "evt_demo_1",
            "event_type": "harsh_brake",
            "trip_meter_km": 37.1,
            "peak_force_g": 0.41,
            "speed_at_event_kmh": 54.0,
        }
    ]
    return json.dumps({"event_count": len(demo_events), "events": demo_events})


@tool
def extract_scoring_features(
    smoothness_logs_json: str,
    harsh_events_json: str,
    trip_duration_minutes: float,
    trip_distance_km: float,
) -> str:
    """Extract and aggregate scoring features from logs/events."""
    try:
        smoothness_data = json.loads(smoothness_logs_json)
        harsh_data = json.loads(harsh_events_json)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"})

    windows = smoothness_data.get("windows", [])
    events = harsh_data.get("events", [])

    if windows:
        jerk_mean_avg = sum(w.get("jerk_mean", 0) for w in windows) / len(windows)
        jerk_max_peak = max(w.get("jerk_max", 0) for w in windows)
        speed_std_avg = sum(w.get("speed_std_dev", 0) for w in windows) / len(windows)
        mean_lateral_g_avg = sum(w.get("mean_lateral_g", 0) for w in windows) / len(
            windows
        )
        max_lateral_g_peak = max(w.get("max_lateral_g", 0) for w in windows)
        mean_rpm_avg = sum(w.get("mean_rpm", 0) for w in windows) / len(windows)
        total_idle_seconds = sum(w.get("idle_seconds", 0) for w in windows)
        duration_seconds = max(trip_duration_minutes * 60, 1)
        idle_ratio = total_idle_seconds / duration_seconds
    else:
        jerk_mean_avg = jerk_max_peak = speed_std_avg = 0.0
        mean_lateral_g_avg = max_lateral_g_peak = mean_rpm_avg = 0.0
        idle_ratio = 0.0

    harsh_brake_count = sum(1 for e in events if e.get("event_type") == "harsh_brake")
    harsh_brake_rate_per_100km = (
        (harsh_brake_count / trip_distance_km) * 100 if trip_distance_km > 0 else 0.0
    )

    return json.dumps(
        {
            "smoothness_features": {
                "jerk_mean_avg": round(jerk_mean_avg, 4),
                "jerk_max_peak": round(jerk_max_peak, 4),
                "speed_std_avg": round(speed_std_avg, 2),
                "mean_lateral_g_avg": round(mean_lateral_g_avg, 3),
                "max_lateral_g_peak": round(max_lateral_g_peak, 3),
                "mean_rpm_avg": round(mean_rpm_avg, 0),
                "idle_ratio": round(idle_ratio, 3),
                "harsh_brake_count": harsh_brake_count,
                "harsh_brake_rate_per_100km": round(harsh_brake_rate_per_100km, 2),
            },
            "raw_smoothness_logs": smoothness_data,
            "raw_harsh_events": harsh_data,
        }
    )


@tool
def score_and_audit_trip(
    trip_id: str,
    smoothness_features: str,
    demographics: str,
    xai_engine: Any = None,
    fairness_auditor: Any = None,
) -> str:
    """Composite operation: score + explain + fairness audit."""
    try:
        features_data = json.loads(smoothness_features)
        demo_data = json.loads(demographics)
    except json.JSONDecodeError:
        return json.dumps({"error": "Invalid JSON input"})

    resolved_xai = xai_engine or _RUNTIME_SERVICES["xai_engine"]
    resolved_fairness = fairness_auditor or _RUNTIME_SERVICES["fairness_auditor"]

    sf = features_data.get("smoothness_features", {})
    jerk_mean = float(sf.get("jerk_mean_avg", 0.0))
    jerk_peak = float(sf.get("jerk_max_peak", 0.0))
    speed_std = float(sf.get("speed_std_avg", 0.0))
    lateral_mean = float(sf.get("mean_lateral_g_avg", 0.0))
    lateral_peak = float(sf.get("max_lateral_g_peak", 0.0))
    mean_rpm = float(sf.get("mean_rpm_avg", 0.0))
    idle_ratio = float(sf.get("idle_ratio", 0.0))

    jerk_component = max(0.0, min(40.0, 40.0 - (jerk_mean * 800.0 + jerk_peak * 8.0)))
    speed_component = max(0.0, min(25.0, 25.0 - speed_std * 0.9))
    lateral_component = max(
        0.0, min(20.0, 20.0 - (lateral_mean * 70.0 + lateral_peak * 15.0))
    )
    engine_component = max(
        0.0, min(15.0, 15.0 - abs(mean_rpm - 1500.0) / 200.0 - idle_ratio * 20.0)
    )
    behaviour_score = round(
        jerk_component + speed_component + lateral_component + engine_component, 1
    )

    if behaviour_score >= 85:
        score_label = "Excellent"
    elif behaviour_score >= 70:
        score_label = "Good"
    elif behaviour_score >= 55:
        score_label = "Average"
    elif behaviour_score >= 40:
        score_label = "Below Average"
    else:
        score_label = "Poor"

    coaching_reasons = []
    harsh_events = features_data.get("raw_harsh_events", {}).get("events", [])
    if harsh_events:
        coaching_reasons.append("Harsh events detected; coaching recommended.")
    if idle_ratio > 0.25:
        coaching_reasons.append("High idle ratio detected; improve idle management.")
    coaching_required = bool(coaching_reasons)

    xai_features = {
        "jerk_mean": jerk_mean,
        "speed_std_dev": speed_std,
        "mean_lateral_g": lateral_mean,
        "idle_ratio": idle_ratio,
    }
    shap_explanation = (
        resolved_xai.explain(xai_features, trip_id=trip_id)
        if resolved_xai is not None
        else {
            "method": "tool_fallback",
            "top_features": [],
            "base_score": 50.0,
            "final_score": behaviour_score,
            "narrative": "Explanation unavailable; fallback mode.",
        }
    )
    fairness_audit = (
        resolved_fairness.audit(behaviour_score, demo_data)
        if resolved_fairness is not None
        else {
            "demographic_parity": "PASS",
            "equalized_odds": "PASS",
            "bias_detected": False,
            "recommendation": "Fairness auditor not configured; fallback pass.",
        }
    )

    return json.dumps(
        {
            "trip_id": trip_id,
            "behaviour_score": behaviour_score,
            "score_label": score_label,
            "score_breakdown": {
                "jerk_component": round(jerk_component, 1),
                "speed_component": round(speed_component, 1),
                "lateral_component": round(lateral_component, 1),
                "engine_component": round(engine_component, 1),
            },
            "shap_explanation": shap_explanation,
            "fairness_audit": fairness_audit,
            "coaching_required": coaching_required,
            "coaching_reasons": coaching_reasons,
        }
    )


SCORING_TOOLS = [
    get_trip_context,
    get_smoothness_logs,
    get_harsh_events,
    extract_scoring_features,
    score_and_audit_trip,
]
