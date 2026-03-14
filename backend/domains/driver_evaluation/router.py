from fastapi import APIRouter, Depends
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from core.database import get_db
from . import models, schemas

router = APIRouter()

@router.get("/scores/{driver_id}", response_model=List[schemas.TripScoreSchema], tags=["evaluation"])
def get_driver_scores(driver_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.TripScore).filter(models.TripScore.driver_id == driver_id).all()
