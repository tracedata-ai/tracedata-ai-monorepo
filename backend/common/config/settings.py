from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Docker / shell often sets unrelated vars (e.g. RESET_DB); do not fail on them.
        extra="ignore",
    )

    # ── API ────────────────────────────────────────────────────────────────
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    debug: bool = True
    project_name: str = "TraceData Backend"
    project_version: str = "0.1.0"
    project_description: str = (
        "AI-powered vehicle telematics and driver advocacy platform."
    )
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"

    # ── Database ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://postgres:postgres@db:5432/tracedata"

    # ── Redis ────────────────────────────────────────────────────────────────
    redis_url: str = "redis://redis:6379/0"
    visualization_buffer_ttl: int = 3600  # 60 minutes for recent events visualization

    # ── Queues (pipeline stage) ─────────────────────────────────────────────
    ingestion_queue: str = "td:ingestion:events"
    orchestrator_queue: str = "td:orchestrator:events"

    # ── Agent Queues (post-dispatch) ────────────────────────────────────────
    safety_queue: str = "td:agent:safety"
    scoring_queue: str = "td:agent:scoring"
    support_queue: str = "td:agent:support"
    sentiment_queue: str = "td:agent:sentiment"

    # ── Celery (Broker / Backend on Redis DB 0 — unified with pipeline) ──────
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    celery_task_serializer: str = "json"
    celery_result_serializer: str = "json"
    celery_accept_content: str = "json"
    celery_task_acks_late: bool = True
    celery_worker_prefetch_multiplier: int = 1
    celery_task_reject_on_worker_lost: bool = True

    # ── Lock TTLs (seconds) — watchdog resets status='processing' after TTL ──
    # Must be >= 2x maximum expected agent runtime
    # status='locked' (HITL) is NEVER reset by watchdog
    lock_ttl_safety: int = 120  # 2 min  — Safety Agent max ~30s
    lock_ttl_scoring: int = 7200  # 2 hr   — Scoring Agent max ~1hr
    lock_ttl_support: int = 1800  # 30 min — DSP Agent max ~10min
    lock_ttl_sentiment: int = 900  # 15 min — Sentiment Agent max ~5min
    lock_ttl_default: int = 600  # 10 min — fallback

    # ── Security ────────────────────────────────────────────────────────────
    secret_key: str = "changeme"
    pii_salt: str = "tracedata-default-salt"
    hmac_secret: str = "tracedata-hmac-secret"

    # ── AI / LLM ────────────────────────────────────────────────────────────
    google_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    # Orchestrator routing fallback behavior:
    # - off: current behavior, no fallback changes
    # - shadow: log fallback candidate, do not alter dispatch
    # - enforce: apply deterministic fallback on invalid routing output
    orchestrator_routing_fallback_mode: str = "off"

    # ── LangSmith ───────────────────────────────────────────────────────────
    langsmith_api_key: str = ""
    langsmith_project: str = "tracedata"
    langsmith_tracing: bool = False
    langchain_verbose: bool = False

    # ── Smoothness ML Model ──────────────────────────────────────────────────
    # Set these to activate ML-based scoring; leave empty to use heuristic fallback.
    # Run scripts/fetch_model_release.py to populate model_bundle/ before building.
    smoothness_model_path: str = "agents/scoring/model_bundle/model.joblib"
    smoothness_model_serving_dir: str = "agents/scoring/model_bundle/serving"
    smoothness_model_release_tag: str = "v.2.0.0.2026155.2"
    smoothness_model_repo: str = "tracedata-ai/tracedata-ai-ml"

    # ── Integrations ─────────────────────────────────────────────────────────
    slack_notifications_enabled: bool = True
    slack_webhook_url: str = ""
    slack_webhook_url_ops_alerts: str = ""
    slack_webhook_url_tracedata_trips: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
