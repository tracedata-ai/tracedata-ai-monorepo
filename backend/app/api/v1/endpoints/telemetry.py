"""
API endpoints for high-level telemetry ingestion and processing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import entities as models
from app.schemas import entities as schemas
from app.agents.shell_pipe import get_shell_graph
from app.core.logging import get_logger
import uuid
import json

router = APIRouter()
logger = get_logger("app.api.v1.endpoints.telemetry")

@router.post("", tags=["telemetry"])
async def ingest_telemetry(payload: schemas.TelemetryPayload, db: Session = Depends(get_db)):
    """
    Ingests vehicle telemetry and triggers the agentic processing pipeline.
    
    Persistence logic handles database storage for frontend testing.
    """
    log = logger.bind(
        event_type=payload.event_type, 
        trip_id=payload.trip_id, 
        driver_id=payload.driver_id
    )
    
    try:
        log.info("Ingesting telemetry event", details=payload.details)
        
        # 1. Persist to TelemetryEvent table
        new_event = models.TelemetryEvent(
            id=uuid.uuid4(),
            trip_id=uuid.UUID(payload.trip_id),
            vehicle_id=uuid.uuid4(), # Placeholder if not in payload
            driver_id=uuid.UUID(payload.driver_id),
            event_type=payload.event_type,
            category=payload.details.get("category", "manual_trigger"),
            priority=payload.details.get("priority", "medium"),
            latitude=payload.details.get("lat"),
            longitude=payload.details.get("lon"),
            details=json.dumps(payload.details)
        )
        
        # Try to find the vehicle_id from the trip if not provided
        trip = db.query(models.Trip).filter(models.Trip.id == new_event.trip_id).first()
        if trip:
            new_event.vehicle_id = trip.vehicle_id
            log = log.bind(vehicle_id=str(trip.vehicle_id))
            
        db.add(new_event)
        db.commit()
        log.info("Telemetry event persisted to database", event_id=str(new_event.id))

        # 2. Trigger Shell Graph (The Agentic part)
        # Note: In the future, this will be moved to a truly separate agent layer/service
        graph = get_shell_graph()
        result = graph.invoke({"input_payload": payload.model_dump(), "response": "", "next_step": ""})
        
        log.info("Agentic processing complete", agent_response=result.get("response"))
        
        return {
            "status": "success",
            "message": "Telemetry persisted and reached Orchestrator",
            "event_id": str(new_event.id),
            "agent_response": result.get("response")
        }
    except Exception as e:
        db.rollback()
        log.error("Telemetry ingestion failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Ingestion Error: {str(e)}")
