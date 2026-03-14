from core.celery_app import celery_app
from core.logging import get_logger
import time

logger = get_logger("domains.driver_wellness.tasks")

@celery_app.task(name="domains.driver_wellness.tasks.generate_coaching")
def generate_coaching(driver_id: str, trip_id: str):
    log = logger.bind(driver_id=driver_id, trip_id=trip_id)
    log.info("Starting background wellness/coaching analysis")
    
    # Simulate high-latency GenAI (RAG + LLM)
    time.sleep(8)
    
    log.info("Wellness analysis complete")
    return {"status": "success", "feedback": "System suggests more regular rest stops."}
