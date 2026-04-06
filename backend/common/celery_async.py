"""
Single event-loop runner for Celery prefork workers.

Calling ``asyncio.run()`` per operation creates a new loop each time; connections
from ``asyncpg`` / ``redis.asyncio`` must stay on one loop for the worker
process lifetime.
"""

from __future__ import annotations

import asyncio
from collections.abc import Coroutine
from typing import Any, TypeVar

T = TypeVar("T")

_WORKER_LOOP: asyncio.AbstractEventLoop | None = None


def run_async(coro: Coroutine[Any, Any, T]) -> T:
    """Run *coro* on a process-wide loop (create/reuse once per worker)."""
    global _WORKER_LOOP
    if _WORKER_LOOP is None or _WORKER_LOOP.is_closed():
        _WORKER_LOOP = asyncio.new_event_loop()
        asyncio.set_event_loop(_WORKER_LOOP)
    return _WORKER_LOOP.run_until_complete(coro)
