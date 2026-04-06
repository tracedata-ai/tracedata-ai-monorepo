"""
Support Celery task — canonical implementation lives in ``agents.driver_support.tasks``.
"""

from agents.driver_support.tasks import generate_coaching

__all__ = ["generate_coaching"]
