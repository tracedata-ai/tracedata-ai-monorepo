"""
Seed script to initialize database tables and populate them with sample data.
"""

import uuid
import json
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, DATABASE_URL
from app.models.entities import Fleet, Driver, Route, Trip, Issue

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
        print(f"Error loading seed_data.json: {e}")
        return None

def create_schemas(drop_existing=False):
    """Create the necessary database schemas. Optionally drop them first."""
    with engine.connect() as conn:
        if drop_existing:
            print("RESET_DB=true: Dropping existing schema...")
            conn.execute(text("DROP SCHEMA IF EXISTS fleet_schema CASCADE;"))
            conn.commit()
        
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS fleet_schema;"))
        conn.commit()
    print("Schemas initialized.")

def seed_data():
    """Seed the database with data from external JSON."""
    data = load_seed_data()
    if not data:
        return

    db = SessionLocal()
    try:
        # 1. Seed Fleet
        if db.query(Fleet).count() == 0:
            print("Seeding Fleet...")
            vehicles = [
                Fleet(id=uuid.uuid4(), vin=f["vin"], license_plate=f["plate"], make=f["make"], model=f["model"], year=str(f["year"]), status="active") 
                for f in data["fleet_data"]
            ]
            db.add_all(vehicles)
            db.commit()
            print(f"Added {len(vehicles)} commercial trucks.")

        # 2. Seed Drivers
        if db.query(Driver).count() == 0:
            print("Seeding Drivers...")
            drivers = [
                Driver(id=uuid.uuid4(), first_name=d["first"], last_name=d["last"], license_number=d["license"], phone=d["phone"], email=d["email"], status="active") 
                for d in data["driver_data"]
            ]
            db.add_all(drivers)
            db.commit()
            print(f"Added {len(drivers)} logistics drivers.")

        # 3. Seed Routes
        if db.query(Route).count() == 0:
            print("Seeding Routes...")
            routes = [
                Route(id=uuid.uuid4(), name=r["name"], start_location=r["start"], end_location=r["end"], estimated_distance=r["dist"], estimated_duration=r["dur"]) 
                for r in data["route_data"]
            ]
            db.add_all(routes)
            db.commit()
            print(f"Added {len(routes)} logistics routes.")

        # Re-fetch for relational seeding
        all_v = db.query(Fleet).all()
        all_d = db.query(Driver).all()
        all_r = db.query(Route).all()

        # 4. Seed Trips
        if db.query(Trip).count() == 0:
            print("Seeding Trips...")
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
            print(f"Added {len(trips)} production trips.")

        # 5. Seed Issues
        if db.query(Issue).count() == 0:
            print("Seeding Issues...")
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
            print(f"Added {len(issues)} fleet maintenance issues.")

    except Exception as e:
        print(f"Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing Database...")
    reset_requested = os.getenv("RESET_DB", "false").lower() == "true"
    
    create_schemas(drop_existing=reset_requested)
    
    # Re-create tables if they don't exist (or were dropped)
    print("Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)
    
    print("Seeding data...")
    seed_data()
    print("Database initialization complete.")
