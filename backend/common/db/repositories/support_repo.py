"""
SENTIMENT & SUPPORT AGENT REPOSITORIES

Layer 1 Enforcement:
  Each agent receives ONLY its repo → impossible to write to other schemas
"""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


class SentimentRepository:
    """SentimentAgent's write operations on owned tables."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def write_feedback_sentiment(
        self,
        trip_id: str,
        driver_id: str,
        feedback_text: str,
        sentiment_score: float,
        sentiment_label: str,
        analysis: dict,
    ) -> str:
        """Write sentiment analysis for feedback.

        Owned table: sentiment_schema.feedback_sentiment

        Returns:
            Sentiment ID
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO sentiment_schema.feedback_sentiment
                    (trip_id, driver_id, feedback_text, sentiment_score, sentiment_label, analysis, created_at)
                    VALUES (:trip_id, :driver_id, :feedback_text, :score, :label, :analysis, :now)
                    RETURNING sentiment_id
                """
                ),
                {
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "feedback_text": feedback_text,
                    "score": sentiment_score,
                    "label": sentiment_label,
                    "analysis": analysis,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            sentiment_id = result.scalar()
            return sentiment_id


class SupportRepository:
    """SupportAgent's write operations on owned tables."""

    def __init__(self, engine: AsyncEngine):
        self._engine = engine

    async def write_coaching(
        self,
        trip_id: str,
        driver_id: str,
        coaching_category: str,
        message: str,
        priority: str = "normal",
    ) -> str:
        """Write coaching message to coaching_schema.

        Owned table: coaching_schema.coaching

        Args:
            trip_id: Trip ID
            driver_id: Driver ID
            coaching_category: Category (e.g., "harsh_brake", "speeding")
            message: Coaching message
            priority: "critical", "high", "normal", "low"

        Returns:
            Coaching ID
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO coaching_schema.coaching
                    (trip_id, driver_id, coaching_category, message, priority, created_at)
                    VALUES (:trip_id, :driver_id, :category, :message, :priority, :now)
                    RETURNING coaching_id
                """
                ),
                {
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "category": coaching_category,
                    "message": message,
                    "priority": priority,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            coaching_id = result.scalar()
            return coaching_id

    async def write_driver_feedback(
        self,
        trip_id: str,
        driver_id: str,
        feedback_type: str,
        content: str,
        status: str = "pending",
    ) -> str:
        """Write driver feedback to coaching_schema.

        Owned table: coaching_schema.driver_feedback

        Returns:
            Feedback ID
        """
        async with self._engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                    INSERT INTO coaching_schema.driver_feedback
                    (trip_id, driver_id, feedback_type, content, status, created_at)
                    VALUES (:trip_id, :driver_id, :feedback_type, :content, :status, :now)
                    RETURNING feedback_id
                """
                ),
                {
                    "trip_id": trip_id,
                    "driver_id": driver_id,
                    "feedback_type": feedback_type,
                    "content": content,
                    "status": status,
                    "now": datetime.now(UTC).replace(tzinfo=None),
                },
            )
            feedback_id = result.scalar()
            return feedback_id

    async def get_coaching(
        self,
        coaching_id: str,
    ) -> dict[str, Any] | None:
        """Read own coaching (for validation)."""
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT * FROM coaching_schema.coaching
                    WHERE coaching_id = :coaching_id
                """
                ),
                {"coaching_id": coaching_id},
            )
            row = result.first()
            return dict(row._mapping) if row else None
