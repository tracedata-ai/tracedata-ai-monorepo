from app.core.celery_app import celery_app
from app.core.logging import get_logger
import time

logger = get_logger("app.tasks.behavior")

@celery_app.task(name="app.tasks.behavior.evaluate_trip")
def evaluate_trip(trip_id: str):
    """
    Asynchronous task to evaluate driver behavior after a trip ends.
    Simulates heavy XGBoost scoring and AIF360 auditing.
    """
    log = logger.bind(trip_id=trip_id)
    log.info("Starting behavior evaluation task")
    
    # Simulate heavy processing
    time.sleep(5) 
    
    log.info("Behavior evaluation complete. Score generated: 88")
    return {"status": "success", "trip_id": trip_id, "score": 88}
