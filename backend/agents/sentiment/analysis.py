"""Pure sentiment analysis helpers shared by the sentiment graph and tests."""

from __future__ import annotations

from typing import Any

EMOTIONS = ("fatigue", "anxiety", "anger", "sadness")


def clamp_score(x: float) -> float:
    return max(0.0, min(1.0, float(x)))


def avg(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def label_trend(current: float, previous_avg: float, delta: float = 0.05) -> str:
    if current > previous_avg + delta:
        return "rising"
    if current < previous_avg - delta:
        return "falling"
    return "stable"


def compute_window_stats(history_rows: list[dict[str, Any]]) -> dict[str, float]:
    per_emotion_scores: dict[str, list[float]] = {emotion: [] for emotion in EMOTIONS}

    for row in history_rows:
        row_scores = row.get("current_scores") if isinstance(row, dict) else None
        if not isinstance(row_scores, dict):
            continue
        for emotion in EMOTIONS:
            raw = row_scores.get(emotion, 0.0)
            try:
                per_emotion_scores[emotion].append(float(raw))
            except (TypeError, ValueError):
                continue

    return {
        f"{emotion}_avg": round(avg(per_emotion_scores[emotion]), 4)
        for emotion in EMOTIONS
    }


def compute_trend(
    current_scores: dict[str, float],
    window_stats: dict[str, float],
) -> dict[str, str]:
    trend: dict[str, str] = {}
    for emotion in EMOTIONS:
        trend[emotion] = label_trend(
            float(current_scores.get(emotion, 0.0)),
            float(window_stats.get(f"{emotion}_avg", 0.0)),
        )
    return trend


def compute_risk_level(
    current_scores: dict[str, float],
    trend: dict[str, str],
) -> float:
    if not current_scores:
        return 0.0

    dominant_emotion = max(
        EMOTIONS,
        key=lambda emotion: float(current_scores.get(emotion, 0.0)),
    )
    risk = float(current_scores.get(dominant_emotion, 0.0))

    if trend.get(dominant_emotion) == "rising":
        risk += 0.05

    return round(clamp_score(risk), 4)


def dominant_emotion_info(current_scores: dict[str, float]) -> tuple[str, float]:
    if not current_scores:
        return ("fatigue", 0.0)
    dominant_emotion = max(
        EMOTIONS,
        key=lambda emotion: float(current_scores.get(emotion, 0.0)),
    )
    return dominant_emotion, round(float(current_scores.get(dominant_emotion, 0.0)), 4)


def sentiment_label_from_risk(risk_level: float) -> str:
    if risk_level >= 0.45:
        return "negative"
    if risk_level > 0.2:
        return "neutral"
    return "positive"
