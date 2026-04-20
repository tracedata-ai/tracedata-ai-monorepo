"""
Sentiment Agent — with scoped repository.

Uses SentimentRepository to ONLY write to sentiment_schema tables.
"""

import logging
from typing import Any

from agents.base.agent import TDAgentBase
from common.cache.reader import CacheReader
from common.db.engine import engine
from common.db.repositories.support_repo import SentimentRepository
from common.llm import OpenAIModel, load_llm
from common.models.security import IntentCapsule
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)

EMOTION_ANCHORS: dict[str, tuple[str, ...]] = {
    "fatigue": ("tired", "fatigue", "exhausted", "drained", "sleepy", "worn out"),
    "anxiety": ("anxious", "nervous", "worried", "uneasy", "tense", "stressed"),
    "anger": ("angry", "frustrated", "irritated", "annoyed", "furious", "mad"),
    "sadness": ("sad", "down", "low", "discouraged", "upset", "disappointed"),
}

SENTIMENT_EXPLANATION_SYSTEM_PROMPT = (
    """You are the Sentiment Explanation Agent in the TraceData platform.
Your task is to explain the emotional assessment result for a truck driver in a simple, professional, business-focused way.

Important rules:
1. Do not calculate or change any scores.
2. Do not infer emotions that are not supported by the provided results.
3. Do not give any medical, psychological, or clinical diagnosis.
4. Keep the explanation clear, supportive, professional, and easy to understand for a business user.
5. Focus on operationally relevant emotional signals such as fatigue, anxiety, anger, sadness, stress, frustration, or emotional stability.
6. If trend information is provided, mention whether the driver's emotional condition appears stable, improving, or worsening.
7. Connect the result to practical operational meaning, such as coaching need, attention level, or support risk.
8. Avoid punishment-oriented language. The tone should be constructive and human-centered.
9. Keep the explanation to 4 sentences when possible.

Output requirements:
- Write one short explanation paragraph in plain English.
- Explain the main emotional signals shown in the results.
- Mention the most important risk-relevant emotional factor if one exists.
- If appropriate, mention whether the recent pattern suggests stability, improvement, or growing concern.
- Make the wording simple, calm, and businesslike.
- Do not output JSON.

Style samples for the explanation paragraph:
1. "The feedback suggests a generally steady emotional state, with no strong signs of escalating stress. The main signal is mild fatigue, which may affect attention if it continues over multiple trips. From an operational standpoint, the driver would benefit from rest and lighter workload scheduling."
2. "The assessment points to some anxiety and tension, but the overall pattern is still manageable. That matters because sustained stress can reduce concentration and responsiveness during busy driving periods. A short coaching conversation and closer follow-up would be appropriate."
3. "The result is mostly stable, with only limited signs of emotional strain. The main factor to watch is frustration, which can become a risk if it builds across trips. The practical response is to monitor the pattern and reinforce a calm driving routine."
4. "The current reading shows a modest decline in emotional stability, driven by stress-related signals rather than a severe concern. This is important operationally because attention and decision quality may be less consistent under pressure. A supportive check-in would help address the issue early."
5. "The sentiment is balanced overall, but there is enough fatigue and irritation in the result to justify attention. The driver is not showing a critical issue, yet the pattern suggests the workload or schedule should be reviewed. A simple follow-up may prevent the signal from getting worse."
""".strip()
)


class SentimentAgent(TDAgentBase):
    """Analyzes driver feedback sentiment."""

    AGENT_NAME = "sentiment"

    def __init__(
        self,
        engine_param=None,
        redis_client: RedisClient | None = None,
    ):
        """Initialize with sentiment-specific repo."""
        super().__init__(engine_param or engine, redis_client)
        self.sentiment_repo = SentimentRepository(self._engine)
        try:
            self._llm = load_llm(OpenAIModel.GPT_4O_MINI).adapter.get_chat_model()
        except Exception as exc:
            logger.warning(
                {
                    "action": "sentiment_llm_unavailable",
                    "error": str(exc),
                }
            )
            self._llm = None

    async def run(self, capsule_data: dict) -> dict[str, Any]:
        capsule = IntentCapsule.model_validate(capsule_data)
        result = await super().run(capsule_data)
        if result.get("status") != "success":
            return result

        from agents.orchestrator.sentiment_followup import (
            schedule_sentiment_ready_if_success,
        )

        await schedule_sentiment_ready_if_success(
            redis=self._redis,
            engine=self._engine,
            trip_id=capsule.trip_id,
        )
        return result

    async def _execute(
        self,
        trip_id: str,
        cache_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Analyze driver feedback sentiment."""
        try:
            raw = CacheReader.by_key_markers(
                cache_data, "trip_context", "current_event"
            )
            trip_context = (
                raw["trip_context"] if isinstance(raw["trip_context"], dict) else None
            )
            current_event = (
                raw["current_event"] if isinstance(raw["current_event"], dict) else None
            )

            driver_id = (
                (trip_context or {}).get("driver_id", "driver_id_placeholder")
                if trip_context
                else "driver_id_placeholder"
            )

            feedback_text = "Sample feedback"
            if isinstance(current_event, dict):
                # "data" comes from get_event_by_id (DB query result);
                # "details" comes from TripEvent.model_dump() — check both.
                data = current_event.get("data") or current_event.get("details") or {}
                feedback_text = str(
                    (data.get("message") if isinstance(data, dict) else None)
                    or current_event.get("notes")
                    or current_event.get("description")
                    or feedback_text
                )

            lower_fb = feedback_text.lower()
            emotion_scores = self._score_emotions(lower_fb)
            sentiment, sentiment_score = self._derive_sentiment(emotion_scores)
            explanation = await self._build_explanation(
                feedback_text=feedback_text,
                sentiment=sentiment,
                emotion_scores=emotion_scores,
            )

            # Write to sentiment_schema (Layer 1: only this repo available)
            sentiment_id = await self.sentiment_repo.write_feedback_sentiment(
                trip_id=trip_id,
                driver_id=driver_id,
                feedback_text=feedback_text,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment,
                analysis={
                    "method": "anchor_heuristic_v1",
                    "emotion_scores": emotion_scores,
                    "explanation": explanation,
                },
            )

            logger.info(
                {
                    "action": "sentiment_analysis_complete",
                    "trip_id": trip_id,
                    "sentiment": sentiment,
                    "sentiment_id": sentiment_id,
                }
            )

            return {
                "status": "success",
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "emotion_scores": emotion_scores,
                "explanation": explanation,
                "sentiment_id": sentiment_id,
                "trip_id": trip_id,
            }

        except Exception as e:
            logger.error(
                {
                    "action": "sentiment_analysis_error",
                    "trip_id": trip_id,
                    "error": str(e),
                }
            )
            raise

    def _get_repos(self) -> dict[str, Any]:
        """Return SentimentAgent's owned repos."""
        return {"sentiment_repo": self.sentiment_repo}

    @staticmethod
    def _score_emotions(lower_feedback: str) -> dict[str, float]:
        """Prototype anchor scoring via keyword hits."""
        scores: dict[str, float] = {}
        for emotion, anchors in EMOTION_ANCHORS.items():
            hits = sum(1 for token in anchors if token in lower_feedback)
            # Keep bounded and simple for prototype behavior.
            scores[emotion] = min(1.0, round(0.2 * hits, 4))
        return scores

    @staticmethod
    def _derive_sentiment(emotion_scores: dict[str, float]) -> tuple[str, float]:
        max_score = max(emotion_scores.values()) if emotion_scores else 0.0
        if max_score >= 0.4:
            return "negative", 0.25
        if max_score > 0.0:
            return "neutral", 0.5
        return "positive", 0.75

    async def _build_explanation(
        self,
        *,
        feedback_text: str,
        sentiment: str,
        emotion_scores: dict[str, float],
    ) -> str:
        """LLM explanation with deterministic fallback."""
        dominant = max(emotion_scores, key=lambda key: emotion_scores[key])
        dominant_score = emotion_scores.get(dominant, 0.0)
        if self._llm is None:
            return (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )

        payload = {
            "text": feedback_text,
            "sentiment": sentiment,
            "current_scores": emotion_scores,
            "window_stats": None,
            "trend": None,
            "risk_level": dominant_score,
        }
        prompt = (
            f"{SENTIMENT_EXPLANATION_SYSTEM_PROMPT}\n\n"
            f"Input:\n{payload}\n\n"
            "Generate the explanation now."
        )
        try:
            response = await self._llm.ainvoke(prompt)
            content = getattr(response, "content", "") or ""
            clean = str(content).strip()
            return clean or (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )
        except Exception as exc:
            logger.warning(
                {
                    "action": "sentiment_explanation_fallback",
                    "error": str(exc),
                }
            )
            return (
                f"Sentiment is {sentiment}. Dominant emotion signal is "
                f"{dominant} ({dominant_score:.2f})."
            )
