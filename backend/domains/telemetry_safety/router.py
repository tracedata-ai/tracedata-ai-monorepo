from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.logging import get_logger
from . import models, schemas
import uuid
import json

router = APIRouter()
logger = get_logger("domains.telemetry_safety.router")

@router.post("/telemetry", tags=["telemetry"])
async def ingest_telemetry(payload: schemas.TelemetryPayload, db: Session = Depends(get_db)):
    """
    Ingests vehicle telemetry and triggers the agentic processing pipeline.
    """
    log = logger.bind(event_type=payload.event_type, trip_id=payload.trip_id, driver_id=payload.driver_id)
    
    try:
        log.info("Ingesting telemetry event", details=payload.details)
        
        new_event = models.TelemetryEvent(
            id=uuid.uuid4(),
            trip_id=uuid.UUID(payload.trip_id),
            vehicle_id=uuid.uuid4(), # Placeholder
            driver_id=uuid.UUID(payload.driver_id),
            event_type=payload.event_type,
            category=payload.details.get("category", "manual_trigger"),
            priority=payload.details.get("priority", "medium"),
            latitude=payload.details.get("lat"),
            longitude=payload.details.get("lon"),
            details=json.dumps(payload.details)
        )
        
        # In a real app, we'd lookup vehicle_id from current session or metadata
        
        db.add(new_event)
        db.commit()
        log.info("Telemetry event persisted", event_id=str(new_event.id))

        # TODO: Trigger Safety Agent (Sync) and Orchestrator
        
        return {
            "status": "success",
            "message": "Telemetry received by Safety Context",
            "event_id": str(new_event.id)
        }
    except Exception as e:
        db.rollback()
        log.error("Ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/fleet", response_model=schemas.FleetList, tags=["fleet"])
def list_fleet(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Fleet)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/routes", response_model=schemas.RouteList, tags=["routes"])
def list_routes(db: Session = Depends(get_db)):
    items = db.query(models.Route).all()
    return {"items": items, "total": len(items)}

@router.get("/trips", response_model=schemas.TripList, tags=["trips"])
def list_trips(db: Session = Depends(get_db)):
    items = db.query(models.Trip).all()
    return {"items": items, "total": len(items)}

@router.get("/issues", response_model=schemas.IssueList, tags=["issues"])
def list_issues(db: Session = Depends(get_db)):
    items = db.query(models.Issue).all()
    return {"items": items, "total": len(items)}
