"""
Sentiment Celery task — canonical implementation lives in ``agents.sentiment.tasks``.
"""

from agents.sentiment.tasks import analyse_feedback

__all__ = ["analyse_feedback"]
