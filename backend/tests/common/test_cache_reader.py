"""Unit tests for ``CacheReader``."""

from common.cache.reader import CacheReader


def test_by_key_markers_first_match_per_marker():
    data = {
        "trips:x:scoring:all_pings": [1, 2],
        "trips:x:scoring:historical_avg": 0.5,
        "trips:x:safety:current_event": {"event_type": "hb"},
    }
    out = CacheReader.by_key_markers(
        data, "all_pings", "historical_avg", "current_event"
    )
    assert out["all_pings"] == [1, 2]
    assert out["historical_avg"] == 0.5
    assert out["current_event"]["event_type"] == "hb"


def test_by_key_markers_missing_returns_none():
    out = CacheReader.by_key_markers({}, "all_pings")
    assert out["all_pings"] is None
