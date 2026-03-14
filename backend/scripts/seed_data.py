"""
Seed script to initialize database tables and populate them with sample data for DDD structure.
"""

import uuid
import json
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import Core Infrastructure
from core.database import Base, DATABASE_URL
from core.logging import setup_logging, get_logger

# Import Domain Models
from domains.telemetry_safety.models import Fleet, Route, Trip, Issue, TelemetryEvent
from domains.driver_wellness.models import Driver, CoachingSession
from domains.driver_evaluation.models import TripScore

# Initialize logging
setup_logging()
logger = get_logger("scripts.seed_data")

# Initialize the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def load_seed_data():
    """Load seed data from the external JSON file."""
    json_path = os.path.join(os.path.dirname(__file__), "seed_data.json")
    try:
        with open(json_path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error("Error loading seed_data.json", error=str(e))
        return None

def create_schemas(drop_existing=False):
    """Create the necessary database schemas. Optionally drop them first."""
    with engine.connect() as conn:
        if drop_existing:
            logger.info("RESET_DB=true: Dropping existing schema...")
            conn.execute(text("DROP SCHEMA IF EXISTS fleet_schema CASCADE;"))
            conn.commit()
        
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS fleet_schema;"))
        conn.commit()
    logger.info("Schemas initialized.")

def seed_data():
    """Seed the database with data from external JSON."""
    data = load_seed_data()
    if not data:
        return

    db = SessionLocal()
    try:
        # 1. Seed Fleet
        if db.query(Fleet).count() == 0:
            logger.info("Seeding Fleet...")
            vehicles = [
                Fleet(
                    id=uuid.uuid4(), 
                    vin=f["vin"], 
                    license_plate=f["plate"], 
                    make=f["make"], 
                    model=f["model"], 
                    year=str(f["year"]), 
                    status="active"
                ) 
                for f in data["fleet_data"]
            ]
            db.add_all(vehicles)
            db.commit()
            logger.info("Fleet seeding complete", count=len(vehicles))

        # 2. Seed Drivers
        if db.query(Driver).count() == 0:
            logger.info("Seeding Drivers...")
            drivers = [
                Driver(
                    id=uuid.uuid4(), 
                    first_name=d["first"], 
                    last_name=d["last"], 
                    license_number=d["license"], 
                    phone=d["phone"], 
                    email=d["email"], 
                    status="active"
                ) 
                for d in data["driver_data"]
            ]
            db.add_all(drivers)
            db.commit()
            logger.info("Drivers seeding complete", count=len(drivers))

        # 3. Seed Routes
        if db.query(Route).count() == 0:
            logger.info("Seeding Routes...")
            routes = [
                Route(
                    id=uuid.uuid4(), 
                    name=r["name"], 
                    start_location=r["start"], 
                    end_location=r["end"], 
                    estimated_distance=r["dist"], 
                    estimated_duration=r["dur"]
                ) 
                for r in data["route_data"]
            ]
            db.add_all(routes)
            db.commit()
            logger.info("Routes seeding complete", count=len(routes))

        # Re-fetch for relational seeding
        all_v = db.query(Fleet).all()
        all_d = db.query(Driver).all()
        all_r = db.query(Route).all()

        # 4. Seed Trips
        if db.query(Trip).count() == 0:
            logger.info("Seeding Trips...")
            trips = []
            for t in data["trip_data"]:
                start_time = None
                end_time = None
                if "hours_ago_start" in t:
                    start_time = datetime.utcnow() - timedelta(hours=t["hours_ago_start"])
                    if "hours_ago_end" in t:
                        end_time = datetime.utcnow() - timedelta(hours=t["hours_ago_end"])
                elif "mins_ago_start" in t:
                    start_time = datetime.utcnow() - timedelta(minutes=t["mins_ago_start"])
                
                trips.append(Trip(
                    id=uuid.uuid4(), 
                    vehicle_id=all_v[t["vehicle_idx"]].id, 
                    driver_id=all_d[t["driver_idx"]].id, 
                    route_id=all_r[t["route_idx"]].id, 
                    status=t["status"],
                    start_time=start_time,
                    end_time=end_time,
                    actual_distance=t.get("dist"),
                    safety_score=t.get("score")
                ))
            db.add_all(trips)
            db.commit()
            logger.info("Trips seeding complete", count=len(trips))

        # 5. Seed Issues
        if db.query(Issue).count() == 0:
            logger.info("Seeding Issues...")
            issues = [
                Issue(
                    id=uuid.uuid4(), 
                    vehicle_id=all_v[i["vehicle_idx"]].id, 
                    issue_type=i["type"], 
                    severity=i["severity"], 
                    description=i["description"], 
                    status=i["status"]
                ) 
                for i in data["issue_data"]
            ]
            db.add_all(issues)
            db.commit()
            logger.info("Issues seeding complete", count=len(issues))

        # Re-fetch trips for relational seeding
        all_t = db.query(Trip).all()

        # 6. Seed Coaching Records
        if db.query(CoachingSession).count() == 0 and "coaching_data" in data:
            logger.info("Seeding Coaching Records...")
            coaching = [
                CoachingSession(
                    id=uuid.uuid4(),
                    driver_id=all_d[c["driver_idx"]].id,
                    trip_id=all_t[c["trip_idx"]].id,
                    coaching_text=c["text"],
                    tone=c["tone"]
                )
                for c in data["coaching_data"]
            ]
            db.add_all(coaching)
            db.commit()
            logger.info("Coaching records seeding complete", count=len(coaching))

        # 7. Seed Telemetry Events
        if db.query(TelemetryEvent).count() == 0 and "telemetry_event_data" in data:
            logger.info("Seeding Telemetry Events...")
            events = []
            for e_data in data["telemetry_event_data"]:
                trip = all_t[e_data["trip_idx"]]
                events.append(TelemetryEvent(
                    id=uuid.uuid4(),
                    trip_id=trip.id,
                    vehicle_id=trip.vehicle_id,
                    driver_id=trip.driver_id,
                    event_type=e_data["type"],
                    category=e_data["category"],
                    priority=e_data["priority"],
                    latitude=e_data["lat"],
                    longitude=e_data["lon"],
                    details=e_data["details"]
                ))
            db.add_all(events)
            db.commit()
            logger.info("Telemetry events seeding complete", count=len(events))

        # 8. Seed Trip Scores (Evaluation Context)
        if db.query(TripScore).count() == 0:
            logger.info("Seeding Trip Scores...")
            scores = []
            for t in all_t:
                if t.status == "completed" and t.safety_score is not None:
                    scores.append(TripScore(
                        id=uuid.uuid4(),
                        trip_id=t.id,
                        driver_id=t.driver_id,
                        overall_score=t.safety_score,
                        fairness_audit_passed="passed"
                    ))
            db.add_all(scores)
            db.commit()
            logger.info("Trip scores seeding complete", count=len(scores))

    except Exception as e:
        logger.error("Error seeding data", error=str(e), exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Initializing Database...")
    reset_requested = os.getenv("RESET_DB", "false").lower() == "true"
    
    create_schemas(drop_existing=reset_requested)
    
    logger.info("Ensuring tables exist...")
    # This will use the Base where all models have been registered
    Base.metadata.create_all(bind=engine)
    
    logger.info("Seeding data...")
    seed_data()
    logger.info("Database initialization complete.")
