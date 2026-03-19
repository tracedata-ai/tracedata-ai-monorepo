"""
TraceData Backend — FastAPI Shared Dependencies.

Dependencies are injected into route handlers via `Depends(...)`.
This file defines the core reusable dependencies.

Pattern: Dependency Injection avoids passing the DB session manually
to every function. FastAPI calls `get_db()` automatically and closes
the session when the request is done.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an async database session for the duration of one HTTP request.

    Usage in a route:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            ...

    The `async with` ensures the session is always closed after the request,
    even if an exception is raised — no connection leaks.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
