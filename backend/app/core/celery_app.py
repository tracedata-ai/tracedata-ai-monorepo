from celery import Celery
import os

# Get Redis URL from environment or default to local for development
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tracedata_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.behavior", "app.tasks.wellness"]
)

# Optional configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300, # 5 minutes max per task
)

if __name__ == "__main__":
    celery_app.start()
