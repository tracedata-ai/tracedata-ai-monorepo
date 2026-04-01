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
from common.redis.client import RedisClient

logger = logging.getLogger(__name__)


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
                feedback_text = str(
                    current_event.get("notes")
                    or current_event.get("description")
                    or current_event.get("event_type")
                    or feedback_text
                )

            sentiment = "neutral"
            sentiment_score = 0.5
            lower_fb = feedback_text.lower()
            if any(w in lower_fb for w in ("great", "thanks", "good", "excellent")):
                sentiment, sentiment_score = "positive", 0.75
            elif any(
                w in lower_fb for w in ("bad", "terrible", "angry", "hate", "awful")
            ):
                sentiment, sentiment_score = "negative", 0.25

            # Write to sentiment_schema (Layer 1: only this repo available)
            sentiment_id = await self.sentiment_repo.write_feedback_sentiment(
                trip_id=trip_id,
                driver_id=driver_id,
                feedback_text=feedback_text,
                sentiment_score=sentiment_score,
                sentiment_label=sentiment,
                analysis={"method": "simple_heuristic"},
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
