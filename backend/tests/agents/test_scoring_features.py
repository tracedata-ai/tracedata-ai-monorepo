"""Offline tests for scoring feature bundle and merge logic (no LLM)."""

from agents.scoring.features import (
    compute_driver_score,
    deterministic_payload_from_bundle,
    extract_feature_bundle,
    merge_graph_json_with_baseline,
    metrics_from_smoothness_details,
)
from agents.scoring.tools import build_scoring_tools
from common.samples.smoothness_batch import reference_smoothness_batch_details


def test_metrics_from_nested_batch_details():
    d = reference_smoothness_batch_details()
    m = metrics_from_smoothness_details(d)
    assert m["jerk_mean"] == 0.008
    assert m["speed_std"] == 8.1
    assert m["window_harsh"] == 0


def test_extract_feature_bundle_nested_smoothness_log():
    pings = [
        {
            "event_type": "smoothness_log",
            "details": reference_smoothness_batch_details(),
        },
    ]
    b = extract_feature_bundle(pings)
    assert b["smoothness_features"]["jerk_mean_avg"] == 0.008
    assert b["smoothness_features"]["speed_std_avg"] == 8.1


def test_window_harsh_counts_add_to_harsh_event_count():
    d = reference_smoothness_batch_details()
    d = dict(d)
    d["longitudinal"] = {**d["longitudinal"], "harsh_brake_count": 2}
    pings = [{"event_type": "smoothness_log", "details": d}]
    b = extract_feature_bundle(pings)
    assert b["smoothness_features"]["harsh_event_count"] == 2


def test_extract_feature_bundle_smoothness():
    pings = [
        {
            "event_type": "smoothness_log",
            "details": {
                "jerk_mean": 0.02,
                "jerk_max": 1.0,
                "speed_std_dev": 10.0,
                "mean_lateral_g": 0.03,
                "max_lateral_g": 0.1,
                "mean_rpm": 1500,
                "idle_seconds": 20,
            },
        },
    ]
    b = extract_feature_bundle(pings)
    assert "smoothness_features" in b
    assert b["smoothness_features"]["jerk_mean_avg"] == 0.02


def test_deterministic_payload_has_score_breakdown():
    bundle = extract_feature_bundle(
        [
            {
                "event_type": "smoothness_log",
                "details": {
                    "jerk_mean": 0.01,
                    "jerk_max": 0.5,
                    "speed_std_dev": 5.0,
                    "mean_lateral_g": 0.02,
                    "max_lateral_g": 0.08,
                    "mean_rpm": 1500,
                    "idle_seconds": 10,
                },
            },
        ]
    )
    p = deterministic_payload_from_bundle(bundle)
    assert 0 <= p["behaviour_score"] <= 100
    assert "jerk_component" in p["score_breakdown"]


def test_merge_graph_json_clamps_score():
    bundle = extract_feature_bundle(
        [
            {
                "event_type": "smoothness_log",
                "details": {
                    "jerk_mean": 0.02,
                    "jerk_max": 1.0,
                    "speed_std_dev": 10.0,
                    "mean_lateral_g": 0.03,
                    "max_lateral_g": 0.1,
                    "mean_rpm": 1500,
                    "idle_seconds": 20,
                },
            },
        ]
    )
    merged = merge_graph_json_with_baseline(
        {"behaviour_score": 999.0, "score_label": "Poor"},
        bundle,
    )
    assert merged["behaviour_score"] <= 100.0
    assert "score_breakdown" in merged


def test_build_scoring_tools_returns_four_tools():
    tools = build_scoring_tools([], {}, {})
    assert len(tools) == 4
    names = [t.name for t in tools]
    assert "get_trip_context_json" in names
    assert "compute_behaviour_score_from_features" in names


def test_compute_driver_score_uses_historical_avg_when_available():
    assert compute_driver_score(80.0, {"rolling_avg_score": 70.0}) == 77.0


def test_compute_driver_score_falls_back_to_trip_score():
    assert compute_driver_score(88.2, {}) == 88.2


def test_extract_feature_bundle_empty_pings_zeroed_features():
    b = extract_feature_bundle([])
    assert b["smoothness_features"]["jerk_mean_avg"] == 0.0
    assert b["smoothness_features"]["harsh_event_count"] == 0


def test_extract_feature_bundle_malformed_details_string_not_dict():
    pings = [{"event_type": "smoothness_log", "details": "not-a-dict"}]
    b = extract_feature_bundle(pings)
    assert isinstance(b, dict)
