"""
Register scoring Celery task when Celery autodiscovers ``agents.scoring``.

Implementation and @app.task live in ``tasks.scoring_tasks`` (single copy).
"""

import tasks.scoring_tasks  # noqa: F401
