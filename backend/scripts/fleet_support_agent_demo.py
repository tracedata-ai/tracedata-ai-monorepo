"""
Optional local demo: Fleet Support Agent + example JSON payload (OpenAI).

Production coaching uses SupportAgent + Redis/Celery + LangGraph tools; this script reuses
SUPPORT_SYSTEM_PROMPT and the same JSON contract (coaching_category, message, priority),
with a standalone override so no tools are invoked.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from agents.driver_support.prompts import (
    SUPPORT_SYSTEM_PROMPT,
    build_support_user_message,
)
from agents.driver_support.tools import (
    baseline_support_coaching,
    merge_support_json_with_baseline,
)

_STANDALONE_INSTRUCT = """

STANDALONE DEMO — no Redis, Celery, or tools. Ignore WORKFLOW steps that name tools.
Use the JSON block in the user message as your only trip/incident context.
Respond with ONLY one JSON object (no markdown fences, no text before or after) with keys
coaching_category, message, priority.
Allowed coaching_category: follow_up, event_based, post_trip, general.
Allowed priority: high, normal, low.
"""


def _load_env() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    for candidate in (repo_root / ".env", backend_dir / ".env"):
        if candidate.is_file():
            load_dotenv(dotenv_path=candidate)
            return
    load_dotenv()


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Parse first JSON object; tolerate ```json fences."""
    raw = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", raw, re.DOTALL)
    if fence:
        try:
            return json.loads(fence.group(1))
        except json.JSONDecodeError:
            pass
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(raw[start : end + 1])
    except json.JSONDecodeError:
        return None


def get_fleet_support_response(fleet_data: dict) -> dict[str, Any]:
    """
    Call the model with production-style prompts; return merged coaching fields
    (same validation as SupportAgent LLM merge).
    """
    _load_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (repo root or backend/.env).")

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    trip_id = str(fleet_data.get("trip_id") or "DEMO-TRIP")
    driver_hint = str(fleet_data.get("driver_id", "unknown"))

    system_prompt = SUPPORT_SYSTEM_PROMPT + _STANDALONE_INSTRUCT
    user_message = (
        build_support_user_message(trip_id, driver_hint)
        + "\n\nIncident and driver context (JSON). Treat as the only context:\n"
        + json.dumps(fleet_data, indent=2)
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.4,
    )
    content = (response.choices[0].message.content or "").strip()
    parsed = _extract_json_object(content)
    baseline = baseline_support_coaching(
        trip_context={"demo_payload": fleet_data},
        coaching_history=[],
        current_event=None,
        scoring_snapshot=None,
        safety_snapshot=None,
    )
    merged = merge_support_json_with_baseline(parsed, baseline)
    return {
        "raw_model_text": content,
        "coaching_category": merged["coaching_category"],
        "message": merged["message"],
        "priority": merged["priority"],
    }


if __name__ == "__main__":
    example_fleet_data = {
        "event_id": "EVT-99821",
        "driver_id": "DRV-4412",
        "trip_metadata": {
            "timestamp": "2026-03-16T14:30:05Z",
            "location": {
                "lat": 1.29027,
                "long": 103.851959,
            },
            "telemetry_incident": "Hard Braking (9.2 m/s²)",
        },
        "driver_input": {
            "text": "harsh brake",
            "category": "safety_incident_appeal",
        },
    }

    print("--- Fleet Support demo (production JSON contract) ---\n")
    result = get_fleet_support_response(example_fleet_data)
    print(
        json.dumps({k: v for k, v in result.items() if k != "raw_model_text"}, indent=2)
    )
    print("\n--- Raw model output ---\n")
    print(result.get("raw_model_text", ""))
