"""
TraceData.ai — SQLAlchemy Async Engine + Session Factory + DeclarativeBase

KEY CONCEPTS:

1. ASYNC ENGINE (asyncpg)
   FastAPI is async — if you use a sync SQLAlchemy engine, every DB call
   blocks the event loop while waiting for I/O. asyncpg uses Python's
   event loop natively: while waiting for Postgres, FastAPI handles other
   requests. In I/O-bound workloads this is a 5-10x throughput difference.

2. SESSION PER REQUEST (get_db dependency)
   Each HTTP request gets its own AsyncSession. The session is committed if
   the handler returns successfully, or rolled back if an exception is raised.
   This prevents dirty state leaking between requests.

3. pool_pre_ping=True
   Before handing out a connection from the pool, SQLAlchemy pings it.
   Without this, stale connections (e.g. after a Postgres restart via
   docker compose restart) silently fail on the first query. With it, bad
   connections are evicted and replaced transparently.

4. expire_on_commit=False
   By default, SQLAlchemy expires all loaded attributes after commit so they
   are re-fetched on next access. In async code this causes "MissingGreenlet"
   errors when you try to access an attribute after the session is closed.
   expire_on_commit=False means attributes remain accessible after commit.

TRACE EXERCISE:
   A POST /trips request creates a new TelemetryRaw row and returns it.
   Trace the exact sequence from request arrival to response:

   1. FastAPI calls get_db() → AsyncSessionLocal() opens a new session
   2. Route handler receives `db: AsyncSession`
   3. Handler creates TelemetryRaw instance, calls db.add(row)
   4. Handler returns the row (not yet committed)
   5. get_db() finally block: await session.commit()  ← row hits Postgres here
   6. Session closes, connection returns to pool

   Q: What happens if step 4 raises ValidationError?
   A: The `except Exception` block calls rollback() → the row is never written.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,    # log all SQL in debug mode — turn off in prod
    pool_size=10,           # max persistent connections
    max_overflow=20,        # extra connections allowed above pool_size (burst)
    pool_pre_ping=True,     # validate connection before use (handles restarts)
)

# ── Session Factory ───────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # keep attributes accessible after commit
    autocommit=False,
    autoflush=False,
)


# ── Declarative Base ──────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    All SQLAlchemy models inherit from this class.
    Alembic discovers tables via Base.metadata in alembic/env.py.
    """
    pass


# ── FastAPI Dependency ────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Inject into route handlers:
        async def create_trip(db: AsyncSession = Depends(get_db)):

    Commits on success, rolls back on any exception — no leaking state.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
