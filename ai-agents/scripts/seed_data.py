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
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS booking_schema;"))
        conn.commit()
    print("Schemas created or already exist.")

def seed_data():
    """Seed the database with 10 entries per table."""
    db = SessionLocal()
    try:
        # 1. Seed Fleet
        if db.query(Fleet).count() == 0:
            print("Seeding Fleet...")
            vehicles = []
            for i in range(1, 11):
                vehicle = Fleet(
                    id=uuid.uuid4(),
                    vin=f"VIN{str(i).zfill(14)}",
                    license_plate=f"SG-TRUCK-{str(i).zfill(3)}",
                    make="Scania" if i % 2 == 0 else "Mercedes",
                    model="R500" if i % 2 == 0 else "Actros",
                    year="2022" if i % 3 == 0 else "2023",
                    status="active"
                )
                vehicles.append(vehicle)
            db.add_all(vehicles)
            db.commit()
            print(f"Added {len(vehicles)} vehicles.")
        
        # 2. Seed Drivers
        if db.query(Driver).count() == 0:
            print("Seeding Drivers...")
            drivers = []
            first_names = ["John", "Jane", "Robert", "Mary", "Michael", "Patricia", "James", "Linda", "David", "Barbara"]
            last_names = ["Tan", "Lim", "Lee", "Wong", "Ng", "Goh", "Chan", "Teo", "Low", "Chia"]
            for i in range(10):
                driver = Driver(
                    id=uuid.uuid4(),
                    first_name=first_names[i],
                    last_name=last_names[i],
                    license_number=f"S{str(i).zfill(7)}X",
                    phone=f"+65 9{str(i).zfill(7)}",
                    email=f"{first_names[i].lower()}.{last_names[i].lower()}@example.com",
                    status="active"
                )
                drivers.append(driver)
            db.add_all(drivers)
            db.commit()
            print(f"Added {len(drivers)} drivers.")

        # 3. Seed Routes
        if db.query(Route).count() == 0:
            print("Seeding Routes...")
            routes = []
            locs = ["Jurong Port", "Changi Airport", "Tuas Depot", "Woodlands Checkpoint", "Pasir Panjang", "Sentosa", "CBD", "Bishan", "Tampines", "Kranji"]
            for i in range(10):
                route = Route(
                    id=uuid.uuid4(),
                    name=f"Route {locs[i]} - {locs[(i+1)%10]}",
                    start_location=locs[i],
                    end_location=locs[(i+1)%10],
                    estimated_distance=15.5 + i,
                    estimated_duration=0.5 + (i * 0.1)
                )
                routes.append(route)
            db.add_all(routes)
            db.commit()
            print(f"Added {len(routes)} routes.")

        # Re-fetch for FKs
        all_vehicles = db.query(Fleet).all()
        all_drivers = db.query(Driver).all()
        all_routes = db.query(Route).all()

        # 4. Seed Trips
        if db.query(Trip).count() == 0:
            print("Seeding Trips...")
            trips = []
            for i in range(10):
                trip = Trip(
                    id=uuid.uuid4(),
                    vehicle_id=all_vehicles[i].id,
                    driver_id=all_drivers[i].id,
                    route_id=all_routes[i].id,
                    status="completed" if i < 8 else "in_progress",
                    start_time=datetime.utcnow() - timedelta(hours=i+1),
                    end_time=datetime.utcnow() - timedelta(hours=i) if i < 8 else None,
                    actual_distance=all_routes[i].estimated_distance + 0.5,
                    safety_score=85.0 + (i % 15)
                )
                trips.append(trip)
            db.add_all(trips)
            db.commit()
            print(f"Added {len(trips)} trips.")

        # 5. Seed Issues
        if db.query(Issue).count() == 0:
            print("Seeding Issues...")
            issues = []
            issue_types = ["Mechanical", "Safety", "Telemetry", "Safety", "Mechanical", "Telemetry", "Other", "Mechanical", "Safety", "Telemetry"]
            severities = ["low", "medium", "high", "low", "medium", "critical", "low", "medium", "high", "low"]
            for i in range(10):
                issue = Issue(
                    id=uuid.uuid4(),
                    vehicle_id=all_vehicles[i].id,
                    trip_id=db.query(Trip).filter(Trip.vehicle_id == all_vehicles[i].id).first().id if i < 5 else None,
                    issue_type=issue_types[i],
                    severity=severities[i],
                    description=f"Automated test issue description for {issue_types[i]}",
                    status="open" if i % 2 == 0 else "resolved"
                )
                issues.append(issue)
            db.add_all(issues)
            db.commit()
            print(f"Added {len(issues)} issues.")

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
