"""AIF360-style fairness contract tests for current scoring behavior."""

from importlib.util import find_spec

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
                "jerk_mean": 0.012,
                "jerk_max": 0.7,
                "speed_std_dev": 7.0,
                "mean_lateral_g": 0.025,
                "max_lateral_g": 0.09,
                "mean_rpm": 1490,
                "idle_seconds": 12,
            },
        }
    ]
    return extract_feature_bundle(pings)


@pytest.mark.xai
@pytest.mark.eval
def test_deterministic_payload_exposes_fairness_audit_shape():
    payload = deterministic_payload_from_bundle(_sample_bundle())
    audit = payload["fairness_audit"]

    assert set(audit.keys()) == {
        "demographic_parity",
        "equalized_odds",
        "bias_detected",
        "recommendation",
    }
    assert isinstance(audit["bias_detected"], bool)


@pytest.mark.xai
@pytest.mark.eval
def test_merge_graph_json_backfills_fairness_audit_when_missing():
    merged = merge_graph_json_with_baseline({"behaviour_score": 88.5}, _sample_bundle())
    assert "fairness_audit" in merged
    assert "demographic_parity" in merged["fairness_audit"]


@pytest.mark.xai
@pytest.mark.external
def test_aif360_dependency_optional_for_local_runs():
    if find_spec("aif360") is None:
        pytest.skip("aif360 not installed; external fairness backend is optional")
    import aif360  # noqa: F401
