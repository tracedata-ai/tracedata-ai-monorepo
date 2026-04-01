"""Helpers for reading pre-warmed agent cache entries (Redis key → JSON dict)."""

from __future__ import annotations

from typing import Any


class CacheReader:
    """Match cache entries by substring of the Redis key (e.g. ``current_event``)."""

    @staticmethod
    def by_key_markers(
        cache_data: dict[str, Any], *markers: str
    ) -> dict[str, Any | None]:
        """
        For each marker, return the value for the first cache key that contains it.

        Example markers: ``\"current_event\"``, ``\"trip_context\"``, ``\"all_pings\"``.
        """
        found: dict[str, Any | None] = {m: None for m in markers}
        for cache_key, value in cache_data.items():
            for m in markers:
                if found[m] is None and m in cache_key:
                    found[m] = value
        return found
