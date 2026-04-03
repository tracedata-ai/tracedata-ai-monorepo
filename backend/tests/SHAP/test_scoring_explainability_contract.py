"""SHAP-style explainability contract tests for scoring outputs."""

import pytest

from agents.scoring.features import (
    deterministic_payload_from_bundle,
    extract_feature_bundle,
    merge_graph_json_with_baseline,
)


def _sample_bundle() -> dict:
    pings = [
        {
            "event_type": "smoothness_log",
            "details": {
                "jerk_mean": 0.015,
                "jerk_max": 0.9,
                "speed_std_dev": 8.5,
                "mean_lateral_g": 0.03,
                "max_lateral_g": 0.11,
                "mean_rpm": 1520,
                "idle_seconds": 15,
            },
        }
    ]
    return extract_feature_bundle(pings)


@pytest.mark.xai
@pytest.mark.eval
def test_deterministic_payload_exposes_shap_explanation_shape():
    payload = deterministic_payload_from_bundle(_sample_bundle())
    explanation = payload["shap_explanation"]

    assert explanation["method"] == "deterministic_heuristic"
    assert isinstance(explanation["top_features"], list)
    assert len(explanation["top_features"]) >= 3
    assert all("feature" in item and "impact" in item for item in explanation["top_features"])


@pytest.mark.xai
@pytest.mark.eval
def test_merge_graph_json_backfills_shap_when_model_omits_it():
    merged = merge_graph_json_with_baseline({"behaviour_score": 91.0}, _sample_bundle())
    assert "shap_explanation" in merged
    assert merged["shap_explanation"]["method"] == "deterministic_heuristic"
