"""
API endpoints for managing core entities (Fleet, Drivers, Routes, Trips, Issues).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import entities as models
from app.schemas import entities as schemas

router = APIRouter()

@router.get("/fleet", response_model=schemas.FleetList, tags=["fleet"])
def list_fleet(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Fleet)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/drivers", response_model=schemas.DriverList, tags=["drivers"])
def list_drivers(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Driver)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/routes", response_model=schemas.RouteList, tags=["routes"])
def list_routes(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Route)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/trips", response_model=schemas.TripList, tags=["trips"])
def list_trips(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Trip)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/issues", response_model=schemas.IssueList, tags=["issues"])
def list_issues(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Issue)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/sentiment", response_model=List[schemas.SentimentSchema], tags=["ai-agents"])
def list_sentiment(db: Session = Depends(get_db)):
    return db.query(models.SentimentRecord).all()

@router.get("/appeals", response_model=List[schemas.AppealSchema], tags=["ai-agents"])
def list_appeals(db: Session = Depends(get_db)):
    return db.query(models.Appeal).all()

@router.get("/coaching", response_model=List[schemas.CoachingSchema], tags=["ai-agents"])
def list_coaching(db: Session = Depends(get_db)):
    return db.query(models.CoachingRecord).all()

@router.get("/telemetry", response_model=List[schemas.TelemetrySchema], tags=["telemetry"])
def list_telemetry_events(db: Session = Depends(get_db)):
    return db.query(models.TelemetryEvent).all()
