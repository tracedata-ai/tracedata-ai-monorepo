from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.config.settings import get_settings

settings = get_settings()
_database_url = settings.database_url
_engine_kwargs = {"echo": settings.debug}

if make_url(_database_url).get_backend_name() != "sqlite":
    _engine_kwargs.update(
        pool_size=10,
        max_overflow=20,
    )

# ── Engine ────────────────────────────────────────────────────────────────────
engine = create_async_engine(
    _database_url,
    **_engine_kwargs,
)

# ── Session Factory ────────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
