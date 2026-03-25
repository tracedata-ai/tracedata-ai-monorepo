"""
TraceData Backend — Async Database Engine & Session Factory.

This module sets up the SQLAlchemy 2.0 async engine. There are two things
created here that are used throughout the app:

  1. `engine`        — The connection pool to PostgreSQL. Created once.
  2. `AsyncSessionLocal` — A factory for producing database sessions.
     Each HTTP request gets its own session (see `app/api/deps.py`).

Why async?
----------
FastAPI is an async framework. If we used a synchronous DB driver, every
database call would BLOCK the event loop, defeating the purpose of async.
`asyncpg` is the non-blocking PostgreSQL driver we use.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

settings = get_settings()

# ── Engine ────────────────────────────────────────────────────────────────────
# `create_async_engine` wraps asyncpg. `echo=True` logs every SQL statement
# to stdout — extremely useful for development, disable in production.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Set DEBUG=false in .env to silence SQL logs
    pool_size=10,  # Max persistent connections in the pool
    max_overflow=20,  # Extra connections allowed during traffic spikes
)

# ── Session Factory ────────────────────────────────────────────────────────────
# `async_sessionmaker` is the factory. Calling `AsyncSessionLocal()` gives you
# a fresh AsyncSession. expire_on_commit=False means loaded objects stay usable
# after a commit (important for returning Pydantic models from the session).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
