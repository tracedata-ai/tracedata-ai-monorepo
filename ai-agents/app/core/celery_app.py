import os
from celery import Celery

# Load Redis URL from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize Celery app
celery_app = Celery(
    "tracedata_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.services.tasks"]
)

# Configuration for concurrency and task execution
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Singapore",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

if __name__ == "__main__":
    celery_app.start()
