"""
Support (Driver Support) Agent — LangGraph tools (sync, closure-bound per invocation).
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool


def baseline_support_coaching(
    trip_context: dict[str, Any] | None,
    coaching_history: list[Any],
    current_event: dict[str, Any] | None,
    scoring_snapshot: Any,
    safety_snapshot: Any,
) -> dict[str, Any]:
    """Deterministic coaching (same structure as pre-LangGraph SupportAgent)."""
    trip_context = trip_context if isinstance(trip_context, dict) else {}
    coaching_history = coaching_history if isinstance(coaching_history, list) else []
    current_event = current_event if isinstance(current_event, dict) else None
    history_n = len(coaching_history)

    if history_n > 0:
        return {
            "coaching_category": "follow_up",
            "message": (
                f"Continuing coaching — {history_n} prior notes on this trip. "
                "Keep applying prior guidance and drive safely."
            ),
            "priority": "normal",
        }
    if current_event:
        evt_type = current_event.get("event_type", "event")
        priority = (
            "high"
            if str(evt_type).lower() in ("harsh_brake", "collision")
            else "normal"
        )
        return {
            "coaching_category": "event_based",
            "message": (
                f"Coaching for {evt_type}: focus on smooth braking, speed, "
                "and following distance."
            ),
            "priority": priority,
        }
    if scoring_snapshot is not None or safety_snapshot is not None:
        score_hint = ""
        if isinstance(scoring_snapshot, dict):
            s = scoring_snapshot.get("score")
            if s is not None:
                score_hint = f" Trip score: {s}."
        return {
            "coaching_category": "post_trip",
            "message": (
                "Post-trip coaching using your score and latest safety summary."
                + score_hint
            ),
            "priority": "normal",
        }
    return {
        "coaching_category": "general",
        "message": "Keep safe driving practices!",
        "priority": "normal",
    }


def merge_support_json_with_baseline(
    parsed: dict[str, Any] | None,
    baseline: dict[str, Any],
) -> dict[str, Any]:
    out = dict(baseline)
    if not parsed:
        return out
    cat = str(parsed.get("coaching_category") or baseline["coaching_category"]).strip()
    if cat not in ("follow_up", "event_based", "post_trip", "general"):
        cat = baseline["coaching_category"]
    msg = (
        str(parsed.get("message") or baseline["message"]).strip() or baseline["message"]
    )
    pr = str(parsed.get("priority") or baseline["priority"]).strip().lower()
    if pr not in ("high", "normal", "low"):
        pr = baseline["priority"]
    out["coaching_category"] = cat
    out["message"] = msg
    out["priority"] = pr
    return out


def build_support_tools(
    trip_context: dict[str, Any] | None,
    coaching_history: list[Any],
    current_event: dict[str, Any] | None,
    scoring_snapshot: Any,
    safety_snapshot: Any,
) -> list:
    trip_context = trip_context if isinstance(trip_context, dict) else {}
    coaching_history = coaching_history if isinstance(coaching_history, list) else []
    current_event = current_event if isinstance(current_event, dict) else None

    @tool
    def get_support_trip_context_json() -> str:
        """Trip context from warmed cache (may include scoring_output / safety_output)."""
        return json.dumps(trip_context)

    @tool
    def get_support_coaching_history_json() -> str:
        """Recent coaching rows for this trip from warmed cache."""
        return json.dumps(coaching_history)

    @tool
    def get_support_current_event_json() -> str:
        """Current event snapshot when present (event-driven coaching)."""
        return json.dumps(current_event if current_event else {})

    @tool
    def compute_baseline_coaching_plan() -> str:
        """Deterministic coaching category, message, and priority."""
        return json.dumps(
            baseline_support_coaching(
                trip_context,
                coaching_history,
                current_event,
                scoring_snapshot,
                safety_snapshot,
            )
        )

    return [
        get_support_trip_context_json,
        get_support_coaching_history_json,
        get_support_current_event_json,
        compute_baseline_coaching_plan,
    ]
