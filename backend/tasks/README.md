# tasks

Celery task definitions for the TraceData multi-agent system.

- **safety_tasks.py**: Task `analyse_event`.
- **scoring_tasks.py**: Task `score_trip`.
- **support_tasks.py**: Task `generate_coaching`.
- **sentiment_tasks.py**: Task `analyse_feedback`.
- **watchdog_tasks.py**: Task `watchdog_stuck_events`.

Note: Each agent's tasks are imported into the specific agent workers at runtime.
