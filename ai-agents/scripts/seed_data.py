"""
Seed script to initialize database tables and populate them with sample data.
"""

import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import Base, DATABASE_URL
from app.models.entities import Fleet, Driver, Route, Trip, Issue

# Initialize the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_schemas():
    """Create the necessary database schemas if they don't exist."""
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS fleet_schema;"))
        conn.commit()
    print("Schemas created or already exist.")

def seed_data():
    """Seed the database with high-quality, hardcoded Singaporean data."""
    db = SessionLocal()
    try:
        # 1. Hardcoded Fleet (Commercial Trucking Context)
        if db.query(Fleet).count() == 0:
            print("Seeding Fleet...")
            fleet_data = [
                {"vin": "ISUZU1" + "X" * 11, "plate": "GBA1234A", "make": "Isuzu", "model": "Giga Heavy Duty", "year": "2023"},
                {"vin": "HINO2" + "X" * 12, "plate": "XW5678B", "make": "Hino", "model": "500 Series", "year": "2022"},
                {"vin": "FUSO3" + "X" * 12, "plate": "YV9011C", "make": "Mitsubishi Fuso", "model": "Canter", "year": "2023"},
                {"vin": "SCANIA4" + "X" * 10, "plate": "TR2233D", "make": "Scania", "model": "R500 Prime Mover", "year": "2021"},
                {"vin": "VOLVO5" + "X" * 11, "plate": "PZ4455E", "make": "Volvo", "model": "FH16", "year": "2024"},
                {"vin": "UD6" + "X" * 14, "plate": "GBB1122F", "make": "UD Trucks", "model": "Quon", "year": "2022"},
                {"vin": "MAN7" + "X" * 13, "plate": "XW3344G", "make": "MAN", "model": "TGX", "year": "2023"},
                {"vin": "MERC8" + "X" * 12, "plate": "SB5566H", "make": "Mercedes-Benz", "model": "Actros", "year": "2024"},
                {"vin": "DAF9" + "X" * 13, "plate": "YT7788I", "make": "DAF", "model": "XF", "year": "2021"},
                {"vin": "KEN10" + "X" * 12, "plate": "ZA9900J", "make": "Kenworth", "model": "T680", "year": "2023"},
            ]
            vehicles = [Fleet(id=uuid.uuid4(), vin=f["vin"], license_plate=f["plate"], make=f["make"], model=f["model"], year=f["year"], status="active") for f in fleet_data]
            db.add_all(vehicles)
            db.commit()
            print(f"Added {len(vehicles)} commercial trucks.")

        # 2. Hardcoded Drivers (Professional Logistics Personnel)
        if db.query(Driver).count() == 0:
            print("Seeding Drivers...")
            driver_data = [
                {"first": "Wei Ming", "last": "Tan", "license": "S1234567A", "phone": "+65 91234567", "email": "wm.tan@tracedata.ai"},
                {"first": "Siti", "last": "Aisha", "license": "S7654321B", "phone": "+65 82345678", "email": "siti.a@tracedata.ai"},
                {"first": "Rajan", "last": "Sivan", "license": "S9876543C", "phone": "+65 93456789", "email": "rajan.s@tracedata.ai"},
                {"first": "Michael", "last": "Wong", "license": "S1122334D", "phone": "+65 84567890", "email": "m.wong@tracedata.ai"},
                {"first": "Chloe", "last": "Lim", "license": "S4433221E", "phone": "+65 95678901", "email": "chloe.lim@tracedata.ai"},
                {"first": "Ahmad", "last": "Hassan", "license": "S5566778F", "phone": "+65 96789012", "email": "ahmad.h@tracedata.ai"},
                {"first": "Priya", "last": "Nair", "license": "S8899001G", "phone": "+65 87890123", "email": "priya.n@tracedata.ai"},
                {"first": "David", "last": "Lee", "license": "S2233445H", "phone": "+65 98901234", "email": "david.l@tracedata.ai"},
                {"first": "Nur", "last": "Aziz", "license": "S3344556I", "phone": "+65 89012345", "email": "nur.a@tracedata.ai"},
                {"first": "Kevin", "last": "Tan", "license": "S6677889J", "phone": "+65 90123456", "email": "kevin.t@tracedata.ai"},
            ]
            drivers = [Driver(id=uuid.uuid4(), first_name=d["first"], last_name=d["last"], license_number=d["license"], phone=d["phone"], email=d["email"], status="active") for d in driver_data]
            db.add_all(drivers)
            db.commit()
            print(f"Added {len(drivers)} professional logistics drivers.")

        # 3. Hardcoded Routes (Industrial & Logistics Context)
        if db.query(Route).count() == 0:
            print("Seeding Routes...")
            route_data = [
                {"name": "Energy Loop (Jurong Island - Tuas)", "start": "Jurong Island Checkpoint", "end": "Tuas Mega Port", "dist": 25.5, "dur": 0.8},
                {"name": "Airfreight Hub (CAC - Keppel)", "start": "Changi Airfreight Centre", "end": "Keppel Distripark", "dist": 22.2, "dur": 0.6},
                {"name": "North-South Corridor (Woodlands - Senoko)", "start": "Woodlands Checkpoint", "end": "Senoko Industrial Estate", "dist": 12.5, "dur": 0.4},
                {"name": "Container Link (Pasir Panjang - Cogent)", "start": "Pasir Panjang Terminal", "end": "Cogent Logistics Hub", "dist": 15.8, "dur": 0.5},
                {"name": "Supply Chain Route (Sungei Kadut - Tampines)", "start": "Sungei Kadut Industrial", "end": "Tampines Logistics Park", "dist": 28.0, "dur": 1.0},
                {"name": "Clementi Logistics Run", "start": "Clementi West", "end": "Pandan Loop", "dist": 5.2, "dur": 0.2},
                {"name": "Seletar Aerospace Link", "start": "Seletar Aerospace Park", "end": "Northpoint Bizhub", "dist": 18.5, "dur": 0.7},
                {"name": "Bedok Distribution Circuit", "start": "Bedok South", "end": "Loyang Offshore Base", "dist": 14.2, "dur": 0.4},
                {"name": "Kranji Agri-Logistics", "start": "Kranji Way", "end": "Lim Chu Kang", "dist": 9.5, "dur": 0.3},
                {"name": "Alexandra Tech Route", "start": "Alexandra Technopark", "end": "Mapletree Business City", "dist": 3.5, "dur": 0.1},
            ]
            routes = [Route(id=uuid.uuid4(), name=r["name"], start_location=r["start"], end_location=r["end"], estimated_distance=r["dist"], estimated_duration=r["dur"]) for r in route_data]
            db.add_all(routes)
            db.commit()
            print(f"Added {len(routes)} logistics routes.")

        # Re-fetch for relational seeding
        all_v = db.query(Fleet).all()
        all_d = db.query(Driver).all()
        all_r = db.query(Route).all()

        # 4. Hardcoded Trips
        if db.query(Trip).count() == 0:
            print("Seeding Trips...")
            trips = [
                Trip(id=uuid.uuid4(), vehicle_id=all_v[0].id, driver_id=all_d[0].id, route_id=all_r[0].id, status="completed", start_time=datetime.utcnow() - timedelta(hours=5), end_time=datetime.utcnow() - timedelta(hours=4), actual_distance=26.1, safety_score=92.5),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[1].id, driver_id=all_d[1].id, route_id=all_r[1].id, status="in_progress", start_time=datetime.utcnow() - timedelta(minutes=30), actual_distance=5.2, safety_score=88.0),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[2].id, driver_id=all_d[2].id, route_id=all_r[2].id, status="completed", start_time=datetime.utcnow() - timedelta(hours=10), end_time=datetime.utcnow() - timedelta(hours=9), actual_distance=12.8, safety_score=95.5),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[3].id, driver_id=all_d[3].id, route_id=all_r[3].id, status="scheduled"),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[4].id, driver_id=all_d[4].id, route_id=all_r[4].id, status="completed", start_time=datetime.utcnow() - timedelta(days=1), end_time=datetime.utcnow() - timedelta(days=1, hours=-1), actual_distance=28.5, safety_score=90.0),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[5].id, driver_id=all_d[5].id, route_id=all_r[5].id, status="completed", start_time=datetime.utcnow() - timedelta(hours=2), end_time=datetime.utcnow() - timedelta(hours=1), actual_distance=5.5, safety_score=98.0),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[6].id, driver_id=all_d[6].id, route_id=all_r[6].id, status="in_progress", start_time=datetime.utcnow() - timedelta(minutes=45), actual_distance=10.2, safety_score=94.0),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[7].id, driver_id=all_d[7].id, route_id=all_r[7].id, status="scheduled"),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[8].id, driver_id=all_d[8].id, route_id=all_r[8].id, status="completed", start_time=datetime.utcnow() - timedelta(days=2), end_time=datetime.utcnow() - timedelta(days=2, hours=-1), actual_distance=10.0, safety_score=91.5),
                Trip(id=uuid.uuid4(), vehicle_id=all_v[9].id, driver_id=all_d[9].id, route_id=all_r[9].id, status="completed", start_time=datetime.utcnow() - timedelta(hours=8), end_time=datetime.utcnow() - timedelta(hours=7), actual_distance=3.8, safety_score=99.0),
            ]
            db.add_all(trips)
            db.commit()
            print(f"Added {len(trips)} production trips.")

        # 5. Hardcoded Issues
        if db.query(Issue).count() == 0:
            print("Seeding Issues...")
            issues = [
                Issue(id=uuid.uuid4(), vehicle_id=all_v[3].id, issue_type="Telemetry", severity="low", description="Axle weight sensor intermittent signal", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[1].id, issue_type="Mechanical", severity="medium", description="Brake air pressure warning low in front-right", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[6].id, issue_type="Safety", severity="high", description="Unexpected rapid deceleration detected via G-sensor", status="investigating"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[0].id, issue_type="Mechanical", severity="low", description="AdBlue level sensor triggered warning", status="resolved"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[8].id, issue_type="Telemetry", severity="medium", description="GPS drift exceeding 50m in industrial zone", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[2].id, issue_type="Mechanical", severity="high", description="Engine coolant temperature spike during heavy load", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[5].id, issue_type="Safety", severity="low", description="Driver fatigue alert triggered (secondary camera)", status="closed"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[4].id, issue_type="Mechanical", severity="medium", description="Liftgate operation delayed", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[7].id, issue_type="Telemetry", severity="low", description="Odometer mismatch with GPS distance", status="open"),
                Issue(id=uuid.uuid4(), vehicle_id=all_v[9].id, issue_type="Mechanical", severity="low", description="Washer fluid level low", status="resolved"),
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
    create_schemas()
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Seeding data...")
    seed_data()
    print("Database initialization complete.")
