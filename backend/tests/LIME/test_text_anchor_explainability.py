"""LIME-style text explainability tests for current sentiment behavior."""

import pytest

from agents.sentiment.agent import EMOTION_ANCHORS, SentimentAgent

pytestmark = pytest.mark.nightly


@pytest.mark.xai
@pytest.mark.eval
def test_anchor_tokens_raise_expected_emotion_scores():
    text = "I feel tired and worried and frustrated after this trip"
    scores = SentimentAgent._score_emotions(text.lower())

    assert scores["fatigue"] > 0.0
    assert scores["anxiety"] > 0.0
    assert scores["anger"] > 0.0


@pytest.mark.xai
@pytest.mark.eval
def test_sentiment_derivation_thresholds_follow_current_contract():
    negative, negative_score = SentimentAgent._derive_sentiment({"anger": 0.4})
    neutral, neutral_score = SentimentAgent._derive_sentiment({"anger": 0.2})
    positive, positive_score = SentimentAgent._derive_sentiment({})

    assert (negative, negative_score) == ("negative", 0.25)
    assert (neutral, neutral_score) == ("neutral", 0.5)
    assert (positive, positive_score) == ("positive", 0.75)


@pytest.mark.xai
@pytest.mark.eval
def test_emotion_anchor_map_has_minimum_coverage():
    expected_emotions = {"fatigue", "anxiety", "anger", "sadness"}
    assert expected_emotions.issubset(set(EMOTION_ANCHORS.keys()))
    for anchors in EMOTION_ANCHORS.values():
        assert len(anchors) >= 4
