"""
SENTIMENT & SUPPORT AGENT REPOSITORIES

Layer 1 Enforcement:
  Each agent receives ONLY its repo -> impossible to write to other schemas
"""

from datetime import UTC, datetime, timedelta
import json
from typing import Any

from common.db.schema_repository import SchemaRepository
from sqlalchemy import text


class SentimentRepository(SchemaRepository):
    """SentimentAgent's write operations on owned tables."""

    async def list_emotion_anchor_keys(self) -> set[str]:
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT anchor_key
                    FROM sentiment_schema.emotion_anchor_embeddings
                """)
            )
            return {str(row[0]) for row in result.fetchall()}

    async def upsert_emotion_anchor(
        self,
        *,
        anchor_key: str,
        emotion: str,
        anchor_text: str,
        embedding_literal: str,
    ) -> None:
        await self._execute_write(
            """
                INSERT INTO sentiment_schema.emotion_anchor_embeddings
                    (anchor_key, emotion, anchor_text, embedding, created_at, updated_at)
                VALUES
                    (:anchor_key, :emotion, :anchor_text, CAST(:embedding AS vector), :now, :now)
                ON CONFLICT (anchor_key) DO UPDATE
                SET emotion = EXCLUDED.emotion,
                    anchor_text = EXCLUDED.anchor_text,
                    embedding = EXCLUDED.embedding,
                    updated_at = :now
            """,
            {
                "anchor_key": anchor_key,
                "emotion": emotion,
                "anchor_text": anchor_text,
                "embedding": embedding_literal,
            },
        )

    async def find_similar_emotion_anchors(
        self,
        *,
        embedding_literal: str,
        limit: int = 8,
    ) -> list[dict[str, Any]]:
        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        anchor_key,
                        emotion,
                        anchor_text,
                        embedding <=> CAST(:embedding AS vector) AS distance
                    FROM sentiment_schema.emotion_anchor_embeddings
                    ORDER BY embedding <=> CAST(:embedding AS vector)
                    LIMIT :limit
                """),
                {
                    "embedding": embedding_literal,
                    "limit": limit,
                },
            )
            return [dict(row._mapping) for row in result.fetchall()]

    async def fetch_recent_feedback_history(
        self,
        *,
        driver_id: str,
        current_timestamp: datetime,
        window_days: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        earliest_dt = current_timestamp - timedelta(days=window_days)

        async with self._engine.connect() as conn:
            result = await conn.execute(
                text("""
                    SELECT
                        sentiment_id,
                        trip_id,
                        driver_id,
                        feedback_text,
                        sentiment_score,
                        sentiment_label,
                        analysis,
                        event_id,
                        device_event_id,
                        COALESCE(submission_timestamp, created_at) AS submission_timestamp
                    FROM sentiment_schema.feedback_sentiment
                    WHERE driver_id = :driver_id
                      AND COALESCE(submission_timestamp, created_at) >= :earliest_dt
                      AND COALESCE(submission_timestamp, created_at) < :current_dt
                    ORDER BY COALESCE(submission_timestamp, created_at) DESC
                    LIMIT :limit
                """),
                {
                    "driver_id": driver_id,
                    "earliest_dt": earliest_dt.replace(tzinfo=None),
                    "current_dt": current_timestamp.replace(tzinfo=None),
                    "limit": limit,
                },
            )

            rows: list[dict[str, Any]] = []
            for row in result.mappings().all():
                analysis = row["analysis"]
                if isinstance(analysis, str):
                    try:
                        analysis = json.loads(analysis)
                    except json.JSONDecodeError:
                        analysis = {}
                elif not isinstance(analysis, dict):
                    analysis = {}

                submission_timestamp = row["submission_timestamp"]
                rows.append(
                    {
                        "driver_id": row["driver_id"],
                        "submission_id": row["event_id"]
                        or row["device_event_id"]
                        or f"sentiment-{row['sentiment_id']}",
                        "timestamp": (
                            submission_timestamp.replace(tzinfo=UTC).isoformat()
                            if submission_timestamp is not None
                            else ""
                        ),
                        "text": row["feedback_text"] or "",
                        "current_scores": analysis.get("current_scores"),
                    }
                )

            rows.sort(key=lambda item: item["timestamp"])
            return rows

    async def write_feedback_sentiment(
        self,
        trip_id: str,
        driver_id: str,
        feedback_text: str,
        sentiment_score: float,
        sentiment_label: str,
        analysis: dict,
        *,
        event_id: str | None = None,
        device_event_id: str | None = None,
        submission_timestamp: datetime | None = None,
        feedback_embedding_literal: str | None = None,
    ) -> str:
        """Write sentiment analysis; returns sentiment_id."""
        params = {
            "trip_id": trip_id,
            "driver_id": driver_id,
            "feedback_text": feedback_text,
            "score": sentiment_score,
            "label": sentiment_label,
            "analysis": json.dumps(analysis),
            "event_id": event_id,
            "device_event_id": device_event_id,
            "submission_timestamp": (
                submission_timestamp.astimezone(UTC).replace(tzinfo=None)
                if submission_timestamp is not None and submission_timestamp.tzinfo
                else submission_timestamp
            ),
        }

        if feedback_embedding_literal is None:
            return await self._execute_write_scalar(
                """
                    INSERT INTO sentiment_schema.feedback_sentiment
                    (
                        trip_id,
                        driver_id,
                        event_id,
                        device_event_id,
                        submission_timestamp,
                        feedback_text,
                        sentiment_score,
                        sentiment_label,
                        analysis,
                        created_at
                    )
                    VALUES
                    (
                        :trip_id,
                        :driver_id,
                        :event_id,
                        :device_event_id,
                        :submission_timestamp,
                        :feedback_text,
                        :score,
                        :label,
                        :analysis,
                        :now
                    )
                    RETURNING sentiment_id
                """,
                params,
            )

        return await self._execute_write_scalar(
            """
                INSERT INTO sentiment_schema.feedback_sentiment
                (
                    trip_id,
                    driver_id,
                    event_id,
                    device_event_id,
                    submission_timestamp,
                    feedback_text,
                    feedback_embedding,
                    sentiment_score,
                    sentiment_label,
                    analysis,
                    created_at
                )
                VALUES
                (
                    :trip_id,
                    :driver_id,
                    :event_id,
                    :device_event_id,
                    :submission_timestamp,
                    :feedback_text,
                    CAST(:feedback_embedding AS vector),
                    :score,
                    :label,
                    :analysis,
                    :now
                )
                RETURNING sentiment_id
            """,
            {
                **params,
                "feedback_embedding": feedback_embedding_literal,
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
