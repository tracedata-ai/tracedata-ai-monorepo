"""Shared async SQLAlchemy helpers for schema-scoped agent repositories."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


class SchemaRepository:
    """Engine helpers: stamped ``created_at``, write + optional RETURNING, single-row read."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    @staticmethod
    def _utc_naive_now() -> datetime:
        return datetime.now(UTC).replace(tzinfo=None)

    def _with_now(self, params: dict[str, Any]) -> dict[str, Any]:
        out = dict(params)
        out.setdefault("now", self._utc_naive_now())
        return out

    async def _execute_write(self, sql: str, params: dict[str, Any]) -> None:
        async with self._engine.begin() as conn:
            await conn.execute(text(sql), self._with_now(params))

    async def _execute_write_scalar(self, sql: str, params: dict[str, Any]) -> Any:
        async with self._engine.begin() as conn:
            result = await conn.execute(text(sql), self._with_now(params))
            return result.scalar()

    async def _fetch_one_mapping(
        self, sql: str, params: dict[str, Any]
    ) -> dict[str, Any] | None:
        async with self._engine.connect() as conn:
            result = await conn.execute(text(sql), params)
            row = result.first()
            return dict(row._mapping) if row else None

    async def _store_embedding(
        self,
        content_type: str,
        source_id: str,
        content: str,
        driver_id: str | None = None,
        trip_id: str | None = None,
    ) -> None:
        """Generate and store a vector embedding. Silently skips on any failure."""
        try:
            from common.embeddings.client import embed_text  # lazy import

            vector = await embed_text(content)
            if vector is None:
                return
            vec_str = "[" + ",".join(f"{x:.8f}" for x in vector) + "]"
            async with self._engine.begin() as conn:
                await conn.execute(
                    text("""
                        INSERT INTO vector_schema.embeddings
                        (content_type, source_id, driver_id, trip_id, content, embedding, created_at)
                        VALUES (:ctype, :sid, :did, :tid, :content, cast(:vec as vector), :now)
                    """),
                    {
                        "ctype": content_type,
                        "sid": source_id,
                        "did": driver_id,
                        "tid": trip_id,
                        "content": content,
                        "vec": vec_str,
                        "now": self._utc_naive_now(),
                    },
                )
        except Exception as exc:
            logger.warning(
                "Embedding storage skipped (%s/%s): %s", content_type, source_id, exc
            )
