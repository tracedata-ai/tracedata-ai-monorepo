"""
Safety Agent — LangGraph tools (sync, closure-bound per Celery invocation).
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from agents.tools.weather_traffic import get_traffic, get_weather


def baseline_safety_assessment(
    current_event: dict[str, Any],
    trip_context: dict[str, Any] | None,
) -> dict[str, Any]:
    """Deterministic severity / action (same heuristic as pre-LangGraph SafetyAgent)."""
    severity_map = current_event.get("severity", "medium")
    sev = {"critical": 1.0, "high": 0.8, "medium": 0.5, "low": 0.2}.get(
        str(severity_map).lower(), 0.5
    )
    if sev >= 0.9:
        action = "emergency_alert"
    elif sev >= 0.7:
        action = "coaching"
    else:
        action = "monitoring"
    decision = "escalate" if sev >= 0.9 else "monitor"
    evt_type = current_event.get("event_type", "unknown")
    return {
        "severity": sev,
        "action": action,
        "decision": decision,
        "reason": f"Baseline: event_type={evt_type}, nominal_severity={severity_map}",
    }


def merge_safety_json_with_baseline(
    parsed: dict[str, Any] | None,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    """Keep LLM output when well-formed; otherwise use baseline."""
    out = dict(baseline)
    if not parsed:
        return out
    try:
        sev = float(parsed.get("severity", baseline["severity"]))
    except (TypeError, ValueError):
        sev = float(baseline["severity"])
    sev = max(0.0, min(1.0, sev))
    action = (
        str(parsed.get("action") or baseline["action"]).strip() or baseline["action"]
    )
    decision = str(parsed.get("decision") or baseline["decision"]).strip().lower()
    if decision not in ("escalate", "monitor"):
        decision = baseline["decision"]
    reason = (
        str(parsed.get("reason") or baseline["reason"]).strip() or baseline["reason"]
    )
    out["severity"] = sev
    out["action"] = action
    out["decision"] = decision
    out["reason"] = reason
    # Reconcile decision with severity if model drifted
    if sev >= 0.9:
        out["decision"] = "escalate"
    elif out["decision"] == "escalate" and sev < 0.85:
        out["decision"] = "monitor"
    return out


def build_safety_tools(
    current_event: dict[str, Any],
    trip_context: dict[str, Any] | None,
) -> list:
    """Tools closed over warmed cache (safe for concurrent workers).

    Includes shared context tools (weather, traffic) for situational reasoning in ``reason``.
    Those implementations are demo/stub data until wired to live providers.
    """
    trip_context = trip_context if isinstance(trip_context, dict) else {}

    @tool
    def get_safety_event_json() -> str:
        """Current telematics / safety event snapshot (orchestrator-warmed JSON)."""
        return json.dumps(current_event if isinstance(current_event, dict) else {})

    @tool
    def get_safety_trip_context_json() -> str:
        """Trip-level context from warmed cache (JSON string)."""
        return json.dumps(trip_context)

    @tool
    def compute_baseline_safety_assessment() -> str:
        """
        Deterministic severity score (0–1), recommended action, and monitor/escalate
        decision from the current event fields. Use as a sanity check or fallback.
        """
        ce = current_event if isinstance(current_event, dict) else {}
        return json.dumps(baseline_safety_assessment(ce, trip_context))

    return [
        get_safety_event_json,
        get_safety_trip_context_json,
        compute_baseline_safety_assessment,
        get_weather,
        get_traffic,
    ]
