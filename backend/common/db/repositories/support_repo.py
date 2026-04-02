"""
SENTIMENT & SUPPORT AGENT REPOSITORIES

Layer 1 Enforcement:
  Each agent receives ONLY its repo -> impossible to write to other schemas
"""

import json

from typing import Any

from common.db.schema_repository import SchemaRepository


class SentimentRepository(SchemaRepository):
    """SentimentAgent's write operations on owned tables."""

    async def write_feedback_sentiment(
        self,
        trip_id: str,
        driver_id: str,
        feedback_text: str,
        sentiment_score: float,
        sentiment_label: str,
        analysis: dict,
    ) -> str:
        """Write sentiment analysis; returns sentiment_id."""
        return await self._execute_write_scalar(
            """
                    INSERT INTO sentiment_schema.feedback_sentiment
                    (trip_id, driver_id, feedback_text, sentiment_score, sentiment_label, analysis, created_at)
                    VALUES (:trip_id, :driver_id, :feedback_text, :score, :label, :analysis, :now)
                    RETURNING sentiment_id
                """,
            {
                "trip_id": trip_id,
                "driver_id": driver_id,
                "feedback_text": feedback_text,
                "score": sentiment_score,
                "label": sentiment_label,
                "analysis": json.dumps(analysis),
            },
        )


class SupportRepository(SchemaRepository):
    """SupportAgent's write operations on owned tables."""

    async def write_coaching(
        self,
        trip_id: str,
        driver_id: str,
        coaching_category: str,
        message: str,
        priority: str = "normal",
    ) -> str:
        """Write coaching message; returns coaching_id."""
        return await self._execute_write_scalar(
            """
                    INSERT INTO coaching_schema.coaching
                    (trip_id, driver_id, coaching_category, message, priority, created_at)
                    VALUES (:trip_id, :driver_id, :category, :message, :priority, :now)
                    RETURNING coaching_id
                """,
            {
                "trip_id": trip_id,
                "driver_id": driver_id,
                "category": coaching_category,
                "message": message,
                "priority": priority,
            },
        )

    async def write_driver_feedback(
        self,
        trip_id: str,
        driver_id: str,
        feedback_type: str,
        content: str,
        status: str = "pending",
    ) -> str:
        """Write driver feedback; returns feedback_id."""
        return await self._execute_write_scalar(
            """
                    INSERT INTO coaching_schema.driver_feedback
                    (trip_id, driver_id, feedback_type, content, status, created_at)
                    VALUES (:trip_id, :driver_id, :feedback_type, :content, :status, :now)
                    RETURNING feedback_id
                """,
            {
                "trip_id": trip_id,
                "driver_id": driver_id,
                "feedback_type": feedback_type,
                "content": content,
                "status": status,
            },
        )

    async def get_coaching(
        self,
        coaching_id: str,
    ) -> dict[str, Any] | None:
        """Read own coaching (for validation)."""
        return await self._fetch_one_mapping(
            """
                    SELECT * FROM coaching_schema.coaching
                    WHERE coaching_id = :coaching_id
                """,
            {"coaching_id": coaching_id},
        )
