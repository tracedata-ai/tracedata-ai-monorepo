"""Celery task modules for TraceData agent workers."""

# Explicit imports ensure Celery autodiscover_tasks("tasks") registers all tasks.
from tasks import (
    safety_tasks,
    scoring_tasks,
    sentiment_tasks,
    support_tasks,
    watchdog_tasks,
)  # noqa: F401
