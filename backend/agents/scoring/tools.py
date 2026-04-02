"""
Scoring tools for LangGraph (sync, closure-bound per Celery invocation).

No module-level mutable context — call build_scoring_tools() inside _execute.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from agents.scoring.features import (
    deterministic_payload_from_bundle,
    extract_feature_bundle,
)


def build_scoring_tools(
    all_pings: list[dict],
    trip_context: dict[str, Any],
    historical_avg: dict[str, Any],
) -> list:
    """Build tool list closed over warmed cache (safe for concurrent workers)."""

    @tool
    def get_trip_context_json() -> str:
        """Trip context from orchestrator-warmed cache (JSON string)."""
        return json.dumps(trip_context if isinstance(trip_context, dict) else {})

    @tool
    def get_historical_avg_json() -> str:
        """Historical / rolling averages from warmed cache (JSON string)."""
        return json.dumps(historical_avg if isinstance(historical_avg, dict) else {})

    @tool
    def extract_smoothness_features_json() -> str:
        """Smoothness feature bundle + harsh-event metadata from all_pings."""
        return json.dumps(extract_feature_bundle(all_pings))

    @tool
    def compute_behaviour_score_from_features(features_bundle_json: str) -> str:
        """
        Deterministic behaviour score from the JSON returned by
        extract_smoothness_features_json. Returns full scoring payload as JSON.
        """
        try:
            bundle = json.loads(features_bundle_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "invalid features JSON"})
        if "smoothness_features" not in bundle:
            return json.dumps({"error": "missing smoothness_features"})
        payload = deterministic_payload_from_bundle(bundle)
        return json.dumps(payload)

    return [
        get_trip_context_json,
        get_historical_avg_json,
        extract_smoothness_features_json,
        compute_behaviour_score_from_features,
    ]


# Backward compat: empty list (tools are built per run via build_scoring_tools)
SCORING_TOOLS: list = []
