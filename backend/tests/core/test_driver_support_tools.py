"""Unit tests: Support Agent deterministic baseline (UC4 same-trip follow-up)."""

from agents.driver_support.tools import baseline_support_coaching


def test_baseline_follow_up_when_coaching_history_nonempty():
    out = baseline_support_coaching(
        trip_context={},
        coaching_history=[{"coaching_id": "c1"}],
        current_event=None,
        scoring_snapshot=None,
        safety_snapshot=None,
    )
    assert out["coaching_category"] == "follow_up"
    assert "prior" in out["message"].lower()
    assert out["priority"] == "normal"
