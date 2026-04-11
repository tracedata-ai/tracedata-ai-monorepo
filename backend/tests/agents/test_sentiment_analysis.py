from datetime import UTC, datetime

from agents.sentiment.agent import SentimentAgent
from agents.sentiment.analysis import (
    compute_risk_level,
    compute_trend,
    compute_window_stats,
    dominant_emotion_info,
    sentiment_label_from_risk,
)


def test_extract_feedback_text_prefers_event_data_message():
    text = SentimentAgent._extract_feedback_text(
        {
            "event_type": "driver_feedback",
            "data": {
                "message": "I feel tired after today's route and frustrated by delays.",
            },
        }
    )

    assert text == "I feel tired after today's route and frustrated by delays."


def test_window_stats_and_trend_follow_notebook_style_contract():
    history_rows = [
        {
            "current_scores": {
                "fatigue": 0.3,
                "anxiety": 0.2,
                "anger": 0.1,
                "sadness": 0.0,
            }
        },
        {
            "current_scores": {
                "fatigue": 0.5,
                "anxiety": 0.1,
                "anger": 0.2,
                "sadness": 0.0,
            }
        },
    ]
    current_scores = {
        "fatigue": 0.6,
        "anxiety": 0.15,
        "anger": 0.25,
        "sadness": 0.05,
    }

    window_stats = compute_window_stats(history_rows)
    trend = compute_trend(current_scores, window_stats)
    risk_level = compute_risk_level(current_scores, trend)
    dominant_emotion, dominant_score = dominant_emotion_info(current_scores)

    assert window_stats["fatigue_avg"] == 0.4
    assert trend["fatigue"] == "rising"
    assert risk_level == 0.65
    assert (dominant_emotion, dominant_score) == ("fatigue", 0.6)
    assert sentiment_label_from_risk(risk_level) == "negative"


def test_extract_submission_timestamp_parses_iso_string():
    ts = SentimentAgent._extract_submission_timestamp(
        {"timestamp": "2026-03-26T10:30:00Z"}
    )

    assert ts == datetime(2026, 3, 26, 10, 30, tzinfo=UTC)
