"""
Optional local demo: Fleet Support Agent persona + example JSON payload (OpenAI).

Production coaching uses SupportAgent + Redis/Celery; this script mirrors the
input shape described in docs/03-agents/34_support_agent.md for quick testing.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def _load_env() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    repo_root = backend_dir.parent
    for candidate in (repo_root / ".env", backend_dir / ".env"):
        if candidate.is_file():
            load_dotenv(dotenv_path=candidate)
            return
    load_dotenv()


def get_fleet_support_response(fleet_data: dict) -> str:
    """Send fleet/incident JSON to an assistant configured as the Fleet Support Agent."""
    _load_env()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set (repo root or backend/.env).")

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = (
        "You are the Fleet Management Support Agent. Your role is to analyze telematics data "
        "and driver reports to provide constructive feedback, safety tips, and educational guidance "
        "to fleet drivers. Your tone should be professional, supportive, and safety-oriented. "
        "Focus on helping the driver improve and grow. Always refer to specific data points provided."
    )

    user_message = (
        "A driver incident has been reported. Please analyze the following fleet data and "
        "provide improvement tips and learning recommendations:\n\n"
        f"```json\n{json.dumps(fleet_data, indent=2)}\n```"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content or ""


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
            "text": "harsh break",
            "category": "safety_incident_appeal",
        },
    }

    print("--- Sending Fleet Data to Support Agent ---\n")
    support_feedback = get_fleet_support_response(example_fleet_data)
    print("--- Support Agent Feedback ---\n")
    print(support_feedback)
