from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "tracedata_tasks",
    broker=REDIS_URL,
    backend=REDIS_URL,
    # Updated include paths for the new DDD structure
    include=[
        "domains.driver_evaluation.tasks", 
        "domains.driver_wellness.tasks"
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
)

if __name__ == "__main__":
    celery_app.start()
