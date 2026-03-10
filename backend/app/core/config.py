"""
TraceData.ai — Application Settings

HOW IT WORKS:
    pydantic-settings reads from the environment first, then falls back to
    the .env file. This means in production you set real env vars and the
    .env file is ignored — zero code change between dev and prod.

DUAL DATABASE URLS — WHY:
    FastAPI is async; blocking the event loop for every DB call kills throughput.
    asyncpg (async) is the runtime driver.

    Alembic's CLI runner is synchronous — it cannot use asyncpg directly
    without a custom event loop setup. psycopg2 (sync) keeps migrations simple.

    Both URLs point to the same database. The driver prefix is the only difference:
        postgresql+asyncpg://...   ← SQLAlchemy runtime
        postgresql+psycopg2://...  ← Alembic CLI
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Don't raise if .env is missing — useful in Docker where real env
        # vars are injected. Set extra="ignore" to allow undeclared env vars.
        extra="ignore",
    )

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/tracedata"
    )
    database_url_sync: str = (
        "postgresql+psycopg2://postgres:postgres@localhost:5432/tracedata"
    )

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Kafka ─────────────────────────────────────────────────────────────────
    # Inside Docker use kafka:29092 — outside Docker use localhost:9092
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_telemetry: str = "fleet.telemetry"

    # ── OpenAI / LangSmith ─────────────────────────────────────────────────────
    openai_api_key: str = ""
    langsmith_api_key: str = ""
    langsmith_project: str = "tracedata"

    # ── App ───────────────────────────────────────────────────────────────────
    secret_key: str = "change-me-before-prod"
    debug: bool = True
    app_name: str = "TraceData.ai"
    app_version: str = "0.1.0"


# Module-level singleton.
# Import this everywhere: `from app.core.config import settings`
# Never instantiate Settings() a second time — reads .env on every instantiation.
settings = Settings()
