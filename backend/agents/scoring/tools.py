"""
Scoring tools for LangGraph (sync, closure-bound per Celery invocation).

No module-level mutable context — call build_scoring_tools() inside _execute.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from langchain_core.tools import tool

from agents.scoring.features import (
    deterministic_payload_from_bundle,
    extract_feature_bundle,
)

if TYPE_CHECKING:
    from agents.scoring.model.loader import SmoothnessBundleLoader


def build_scoring_tools(
    all_pings: list[dict],
    trip_context: dict[str, Any],
    historical_avg: dict[str, Any],
    ml_scorer: SmoothnessBundleLoader | None = None,
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
        Heuristic behaviour score from the JSON returned by
        extract_smoothness_features_json. Use score_with_ml_model instead
        when the ML bundle is available — this is the deterministic fallback.
        Returns full scoring payload as JSON.
        """
        try:
            bundle = json.loads(features_bundle_json)
        except json.JSONDecodeError:
            return json.dumps({"error": "invalid features JSON"})
        if "smoothness_features" not in bundle:
            return json.dumps({"error": "missing smoothness_features"})
        payload = deterministic_payload_from_bundle(bundle)
        return json.dumps(payload)

    @tool
    def score_with_ml_model() -> str:
        """
        Score the trip using the trained smoothness ML model (real SHAP attributions).

        Reads smoothness_log windows directly from the warmed cache and returns:
        - trip_smoothness_score: float [0–100]
        - explanation.feature_attributions: ranked SHAP values per feature
        - explanation.worst_window_index: which 10-min window hurt the score most
        - explanation.contract_version: pinned model version for audit

        Prefer this over compute_behaviour_score_from_features when available.
        Falls back gracefully with an error key if the bundle is not loaded.
        """
        if ml_scorer is None:
            return json.dumps(
                {
                    "error": "ml_model_not_loaded",
                    "reason": "Bundle not present — run scripts/fetch_model_release.py",
                    "fallback": "use compute_behaviour_score_from_features",
                }
            )

        envelopes = [
            p.get("details", {})
            for p in all_pings
            if str(p.get("event_type", "")).lower() == "smoothness_log"
        ]
        if not envelopes:
            return json.dumps(
                {
                    "error": "no_smoothness_log_envelopes",
                    "fallback": "use compute_behaviour_score_from_features",
                }
            )

        try:
            result = ml_scorer.score_trip(envelopes)
            return json.dumps(result)
        except Exception as exc:
            return json.dumps({"error": "ml_score_failed", "detail": str(exc)})

    return [
        get_trip_context_json,
        get_historical_avg_json,
        extract_smoothness_features_json,
        score_with_ml_model,
        compute_behaviour_score_from_features,
    ]


# Backward compat: empty list (tools are built per run via build_scoring_tools)
SCORING_TOOLS: list = []
