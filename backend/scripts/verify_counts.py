import os
import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tracedata")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def verify_data():
    tables = [
        "fleet", "drivers", "routes", "trips", "issues", 
        "coaching_records", "telemetry_events", "trip_scores"
    ]
    
    results = {}
    with engine.connect() as conn:
        for table in tables:
            try:
                res = conn.execute(text(f"SELECT count(*) FROM fleet_schema.{table}"))
                count = res.scalar()
                results[table] = count
            except Exception as e:
                results[table] = f"Error: {str(e)}"
    
    print("--- Database Verification Results ---")
    for table, count in results.items():
        print(f"Table {table:18}: {count}")
    print("-------------------------------------")

if __name__ == "__main__":
    verify_data()
