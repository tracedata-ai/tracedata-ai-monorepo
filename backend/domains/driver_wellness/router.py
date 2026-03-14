from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from core.database import get_db
from . import models, schemas

router = APIRouter()

@router.get("/drivers", response_model=schemas.DriverList, tags=["drivers"])
def list_drivers(db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    query = db.query(models.Driver)
    total = query.count()
    items = query.offset(skip).limit(limit).all()
    return {"items": items, "total": total}

@router.get("/coaching/{driver_id}", response_model=List[schemas.CoachingSchema], tags=["wellness"])
def get_driver_coaching(driver_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.CoachingSession).filter(models.CoachingSession.driver_id == driver_id).all()
