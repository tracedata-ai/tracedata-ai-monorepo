"""
TraceData — Feedback Agent
===========================
Generates personalised, constructive driver-coaching feedback based on
trip telemetry and behaviour scores.

Usage
-----
::

    from agents.feedback import FeedbackAgent

    agent = FeedbackAgent()
    result = agent.invoke(
        "Driver D-042 had 5 harsh-braking events and 2 speeding incidents "
        "on their last trip.  Generate a coaching message.",
        thread_id="feedback-D042-session1",
    )
    print(result["messages"][-1].content)
"""

from __future__ import annotations

from typing import Any

from langchain_core.tools import tool

from agents.base import BaseAgent

# ---------------------------------------------------------------------------
# Feedback tools
# ---------------------------------------------------------------------------


@tool
def format_coaching_report(
    driver_id: str,
    score: float,
    harsh_braking: int,
    speeding: int,
    harsh_cornering: int,
    trip_distance_km: float,
) -> dict[str, Any]:
    """Produce a structured coaching report dict for a driver.

    Parameters
    ----------
    driver_id:
        Unique identifier of the driver.
    score:
        Overall behaviour score (0–100, higher is better).
    harsh_braking:
        Number of harsh-braking events on the scored trip(s).
    speeding:
        Number of speeding events.
    harsh_cornering:
        Number of harsh-cornering events.
    trip_distance_km:
        Total distance covered in kilometres.

    Returns
    -------
    dict
        Structured report suitable for display or further processing.
    """
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")

    risk_level = "low" if score >= 80 else "medium" if score >= 60 else "high"

    total_incidents = harsh_braking + speeding + harsh_cornering
    incidents_per_100km = (
        round(total_incidents / trip_distance_km * 100, 2)
        if trip_distance_km > 0
        else 0.0
    )

    return {
        "driver_id": driver_id,
        "overall_score": round(score, 1),
        "risk_level": risk_level,
        "incidents": {
            "harsh_braking": harsh_braking,
            "speeding": speeding,
            "harsh_cornering": harsh_cornering,
            "total": total_incidents,
        },
        "incidents_per_100km": incidents_per_100km,
        "trip_distance_km": trip_distance_km,
        "improvement_areas": _identify_improvement_areas(
            harsh_braking, speeding, harsh_cornering
        ),
    }


def _identify_improvement_areas(
    harsh_braking: int,
    speeding: int,
    harsh_cornering: int,
) -> list[str]:
    areas: list[str] = []
    if harsh_braking > 2:
        areas.append("braking smoothness")
    if speeding > 0:
        areas.append("speed compliance")
    if harsh_cornering > 2:
        areas.append("cornering technique")
    return areas or ["general maintenance — performance is good"]


# ---------------------------------------------------------------------------
# Concrete agent
# ---------------------------------------------------------------------------


class FeedbackAgent(BaseAgent):
    """Generates empathetic, actionable driver-coaching feedback.

    The agent uses ``format_coaching_report`` to structure the raw telemetry
    data before composing a personalised coaching message.
    """

    SYSTEM_PROMPT = """You are the TraceData Feedback Agent — a professional \
driver-coaching assistant embedded in a fleet-management platform.

Your responsibilities:
1. Analyse driving behaviour data provided by the fleet manager or the
   Orchestrator Agent.
2. Call `format_coaching_report` to produce a structured summary before
   composing the coaching message.
3. Compose a personalised, constructive, and encouraging coaching message
   for the driver.

Tone guidelines:
- Professional but empathetic.
- Focus on improvement, not blame.
- Be specific: reference actual incident counts and distances.
- Keep messages concise (≤ 200 words unless asked for more detail).

Output format:
1. Structured report (from tool).
2. Personalised coaching message (3–5 sentences).
3. One prioritised improvement tip.
"""

    tools = [format_coaching_report]
