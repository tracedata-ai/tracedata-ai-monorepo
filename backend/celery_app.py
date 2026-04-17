"""
Celery Application — single instance imported by all workers.

Every agent container imports this module to register tasks.
The Orchestrator imports it to call apply_async.

Broker:  Redis DB 0 (unified with pipeline queues)
Backend: Redis DB 0

Location: backend/celery_app.py
"""

from celery import Celery

from common.config.settings import get_settings

settings = get_settings()

# ── App instance ──────────────────────────────────────────────────────────────

app = Celery("tracedata")

app.conf.update(
    # ── Broker / backend ──────────────────────────────────────────────────────
    broker_url=settings.celery_broker_url,
    result_backend=settings.celery_result_backend,
    # ── Serialisation ────────────────────────────────────────────────────────
    task_serializer=settings.celery_task_serializer,
    result_serializer=settings.celery_result_serializer,
    accept_content=[settings.celery_accept_content],
    # ── Reliability ──────────────────────────────────────────────────────────
    # task_acks_late: task is only acknowledged AFTER completion.
    # If the worker crashes mid-task, the task is requeued.
    task_acks_late=settings.celery_task_acks_late,
    # worker_prefetch_multiplier=1: worker only fetches one task at a time.
    # This preserves ZSet priority ordering — a CRITICAL task won't be
    # blocked behind a LOW task that was pre-fetched by the same worker.
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    # task_reject_on_worker_lost: requeue task if worker loses heartbeat.
    task_reject_on_worker_lost=settings.celery_task_reject_on_worker_lost,
    # ── Redis key organization ────────────────────────────────────────────────
    # Kombu bindings use this prefix: celery:binding:{queue_name}
    # Task results use this prefix: celery:result:{task_id}
    broker_transport_options={
        "master_name": "celery",  # Namespace for Kombu channels/bindings
        "key_prefix": "celery:",  # Prefix for all Celery Redis keys
    },
    # ── Queue routing ─────────────────────────────────────────────────────────
    # Each agent has its own queue. Independent scaling, no interference.
    task_routes={
        "tasks.safety_tasks.analyse_event": {"queue": settings.safety_queue},
        "tasks.scoring_tasks.score_trip": {"queue": settings.scoring_queue},
        "tasks.support_tasks.generate_coaching": {"queue": settings.support_queue},
        "tasks.sentiment_tasks.analyse_feedback": {"queue": settings.sentiment_queue},
        # Watchdog tasks run on the safety worker (low-load, singleton).
        "tasks.watchdog_tasks.reset_stuck_events": {"queue": settings.safety_queue},
        "tasks.watchdog_tasks.publish_queue_depths": {"queue": settings.safety_queue},
        "tasks.watchdog_tasks.rescore_unscored_trips": {"queue": settings.safety_queue},
        "tasks.watchdog_tasks.requeue_stuck_received_events": {
            "queue": settings.safety_queue
        },
        "tasks.watchdog_tasks.requeue_stuck_trips": {"queue": settings.safety_queue},
    },
    # ── Beat schedule (watchdog) ──────────────────────────────────────────────
    beat_schedule={
        "watchdog-stuck-events": {
            "task": "tasks.watchdog_tasks.reset_stuck_events",
            "schedule": 120.0,  # every 2 minutes
        },
        "queue-depth-monitor": {
            "task": "tasks.watchdog_tasks.publish_queue_depths",
            "schedule": 60.0,  # every 1 minute
        },
        "rescore-unscored-trips": {
            "task": "tasks.watchdog_tasks.rescore_unscored_trips",
            "schedule": 300.0,  # every 5 minutes
        },
        "requeue-stuck-received-events": {
            "task": "tasks.watchdog_tasks.requeue_stuck_received_events",
            "schedule": 300.0,  # every 5 minutes
        },
        "requeue-stuck-trips": {
            "task": "tasks.watchdog_tasks.requeue_stuck_trips",
            "schedule": 600.0,  # every 10 minutes
        },
    },
    # ── Timezone ─────────────────────────────────────────────────────────────
    timezone="UTC",
    enable_utc=True,
)

# ── Task autodiscovery ────────────────────────────────────────────────────────
# Celery will find tasks in:
# - agents/*/tasks.py (agent-specific tasks)
# - tasks/*.py (standalone task files)
app.autodiscover_tasks(
    [
        "agents.safety",
        "agents.scoring",
        "agents.driver_support",
        "agents.sentiment",
        "tasks",  # Discover tasks from tasks/ package
    ]
)
