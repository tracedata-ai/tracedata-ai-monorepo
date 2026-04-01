"""Shared async SQLAlchemy helpers for schema-scoped agent repositories."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


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
