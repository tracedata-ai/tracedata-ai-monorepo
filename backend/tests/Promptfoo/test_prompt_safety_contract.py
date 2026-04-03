"""Promptfoo-style safety tests adapted to current backend prompt contracts."""

import pytest

from agents.sentiment.agent import SENTIMENT_EXPLANATION_SYSTEM_PROMPT, SentimentAgent


@pytest.mark.xai
@pytest.mark.eval
def test_sentiment_system_prompt_contains_safety_constraints():
    required_clauses = [
        "Do not calculate or change any scores",
        "Do not give any medical, psychological, or clinical diagnosis",
        "Do not output JSON",
    ]
    for clause in required_clauses:
        assert clause in SENTIMENT_EXPLANATION_SYSTEM_PROMPT


@pytest.mark.asyncio
@pytest.mark.xai
@pytest.mark.eval
async def test_build_explanation_falls_back_without_llm():
    # Avoid full agent init and network dependency; exercise current fallback contract only.
    agent = object.__new__(SentimentAgent)
    agent._llm = None

    text = "I am tired and stressed after a difficult route."
    sentiment = "negative"
    emotion_scores = {"fatigue": 0.4, "anxiety": 0.2, "anger": 0.0, "sadness": 0.0}

    explanation = await agent._build_explanation(
        feedback_text=text,
        sentiment=sentiment,
        emotion_scores=emotion_scores,
    )

    assert "Sentiment is negative." in explanation
    assert "Dominant emotion signal is fatigue" in explanation
