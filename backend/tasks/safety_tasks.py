"""
Safety Celery task — canonical implementation lives in ``agents.safety.tasks``.
"""

from agents.safety.tasks import analyse_event

__all__ = ["analyse_event"]
