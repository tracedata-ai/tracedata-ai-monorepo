"""
Unified TraceData test data management tool.

Consolidates database seeding, telemetry event generation, and test data loading.

Usage:
  python send_telemetry.py db              # Seed database with drivers, vehicles, routes, trips
  python send_telemetry.py trips           # Send 10 complete realistic trips
  python send_telemetry.py diverse         # Send 6 diverse event types (agent routing test)
  python send_telemetry.py random          # Send 20 random telemetry events
  python send_telemetry.py all             # All of the above (default)
"""

import asyncio
import json
import random
import sys
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import redis.asyncio as redis
from sqlalchemy import delete

from api.models.driver import Driver
from api.models.fleet import Vehicle
from api.models.route import Route
from api.models.tenant import Tenant
from api.models.trip import Trip
from common.db.engine import AsyncSessionLocal
from core.logging import get_logger

logger = get_logger(__name__)

# ────────────────────────────────────────────────────────────────────────────────
# DATABASE SEED DATA
# ────────────────────────────────────────────────────────────────────────────────

SEED_DATA = {
    "tenants": [
        {
            "key": "t1",
            "name": "Singapore Logistics Hub",
            "contact_email": "ops@sg-logistics.com.sg",
            "status": "active",
        },
        {
            "key": "t2",
            "name": "Tuas Haulage Solutions",
            "contact_email": "fleet@tuas-haulage.com",
            "status": "active",
        },
    ],
    "drivers": [
        {
            "key": "d1",
            "tenant": "t1",
            "first_name": "Wei Kiat",
            "last_name": "Tan",
            "email": "weikiat.tan@sg-logistics.com.sg",
            "license_number": "S1234567A",
            "experience_level": "expert",
        },
        {
            "key": "d2",
            "tenant": "t1",
            "first_name": "Siti",
            "last_name": "Aminah",
            "email": "siti.a@sg-logistics.com.sg",
            "license_number": "S7654321B",
            "experience_level": "intermediate",
        },
        {
            "key": "d3",
            "tenant": "t2",
            "first_name": "Muthu",
            "last_name": "Kumaran",
            "email": "muthu.k@tuas-haulage.com",
            "license_number": "S9876543C",
            "experience_level": "novice",
        },
    ],
    "vehicles": [
        {
            "key": "v1",
            "tenant": "t1",
            "license_plate": "SBA 1234 A",
            "make": "Isuzu",
            "model": "N-Series (ELF)",
            "year": 2022,
            "status": "active",
        },
        {
            "key": "v2",
            "tenant": "t1",
            "license_plate": "SGE 5678 B",
            "make": "Mitsubishi Fuso",
            "model": "Canter",
            "year": 2021,
            "status": "active",
        },
        {
            "key": "v3",
            "tenant": "t2",
            "license_plate": "SMB 9101 C",
            "make": "Hino",
            "model": "300 Series",
            "year": 2023,
            "status": "active",
        },
    ],
    "routes": [
        {
            "key": "r1",
            "tenant": "t1",
            "name": "West-East Corridor",
            "start_location": "Tuas Logistic Hub",
            "end_location": "Changi Airfreight Centre",
            "distance_km": Decimal("45.5"),
            "route_type": "highway",
        },
        {
            "key": "r2",
            "tenant": "t2",
            "name": "Northern Loop",
            "start_location": "Woodlands Industrial Park",
            "end_location": "Jurong Port",
            "distance_km": Decimal("28.2"),
            "route_type": "mixed",
        },
    ],
    "trips": [
        {
            "key": "trip1",
            "tenant": "t1",
            "driver": "d1",
            "vehicle": "v1",
            "route": "r1",
            "status": "active",
        },
        {
            "key": "trip2",
            "tenant": "t1",
            "driver": "d2",
            "vehicle": "v2",
            "route": "r1",
            "status": "completed",
            "safety_score": Decimal("88.5"),
            "score_explanation": "Clean trip with minor idling at Changi.",
        },
        {
            "key": "trip3",
            "tenant": "t2",
            "driver": "d3",
            "vehicle": "v3",
            "route": "r2",
            "status": "completed",
            "safety_score": Decimal("92.0"),
            "score_explanation": "Excellent safe driving. No violations.",
        },
    ],
}

# Random telemetry configuration
TRUCK_IDS = ["TRUCK-SG-1234", "TRUCK-SG-5678", "TRUCK-SG-9101", "TRUCK-JB-2022"]
DRIVER_IDS = ["DRIVER-SG-77", "DRIVER-SG-88", "DRIVER-SG-99", "DRIVER-JB-11"]
TRIP_IDS = ["TRIP-LIVE-001", "TRIP-LIVE-002", "TRIP-LIVE-003"]
LOCATIONS = [
    {"lat": 1.2863, "lon": 103.8519},  # Marina Bay
    {"lat": 1.3521, "lon": 103.8198},  # Raffles
    {"lat": 1.2902, "lon": 103.8519},  # Pioneer
    {"lat": 1.3424, "lon": 103.7618},  # Changi
]

EVENT_TYPES_CONFIG = {
    "collision": {
        "priority": "critical",
        "category": "safety_incidents",
        "details": {"impact_severity": "medium"},
    },
    "rollover": {
        "priority": "critical",
        "category": "safety_incidents",
        "details": {"angle_degrees": 45},
    },
    "harsh_brake": {
        "priority": "high",
        "category": "safety_incidents",
        "details": {"deceleration_g": 0.92},
    },
    "harsh_corner": {
        "priority": "high",
        "category": "safety_incidents",
        "details": {"lateral_g": 0.87},
    },
    "speeding": {
        "priority": "medium",
        "category": "safety_violations",
        "details": {"speed_kmh": 105},
    },
    "smoothness_log": {
        "priority": "low",
        "category": "normal_operation",
        "details": {"smoothness_score": 0.85},
    },
}

# ────────────────────────────────────────────────────────────────────────────────
# DATABASE SEEDING
# ────────────────────────────────────────────────────────────────────────────────


async def seed_database():
    """Populate database with test data."""
    async with AsyncSessionLocal() as session:
        # Clear existing data
        await session.execute(delete(Trip))
        await session.execute(delete(Route))
        await session.execute(delete(Vehicle))
        await session.execute(delete(Driver))
        await session.execute(delete(Tenant))
        await session.commit()

        # Seed tenants
        tenant_map = {}
        for tenant_data in SEED_DATA["tenants"]:
            tenant = Tenant(
                key=tenant_data["key"],
                name=tenant_data["name"],
                contact_email=tenant_data["contact_email"],
                status=tenant_data["status"],
            )
            session.add(tenant)
            tenant_map[tenant_data["key"]] = tenant
        await session.commit()

        # Seed drivers
        driver_map = {}
        for driver_data in SEED_DATA["drivers"]:
            tenant = tenant_map[driver_data["tenant"]]
            driver = Driver(
                key=driver_data["key"],
                tenant_id=tenant.id,
                first_name=driver_data["first_name"],
                last_name=driver_data["last_name"],
                email=driver_data["email"],
                license_number=driver_data["license_number"],
                experience_level=driver_data["experience_level"],
            )
            session.add(driver)
            driver_map[driver_data["key"]] = driver
        await session.commit()

        # Seed vehicles
        vehicle_map = {}
        for vehicle_data in SEED_DATA["vehicles"]:
            tenant = tenant_map[vehicle_data["tenant"]]
            vehicle = Vehicle(
                key=vehicle_data["key"],
                tenant_id=tenant.id,
                license_plate=vehicle_data["license_plate"],
                make=vehicle_data["make"],
                model=vehicle_data["model"],
                year=vehicle_data["year"],
                status=vehicle_data["status"],
            )
            session.add(vehicle)
            vehicle_map[vehicle_data["key"]] = vehicle
        await session.commit()

        # Seed routes
        route_map = {}
        for route_data in SEED_DATA["routes"]:
            tenant = tenant_map[route_data["tenant"]]
            route = Route(
                key=route_data["key"],
                tenant_id=tenant.id,
                name=route_data["name"],
                start_location=route_data["start_location"],
                end_location=route_data["end_location"],
                distance_km=route_data["distance_km"],
                route_type=route_data["route_type"],
            )
            session.add(route)
            route_map[route_data["key"]] = route
        await session.commit()

        # Seed trips
        for trip_data in SEED_DATA["trips"]:
            tenant = tenant_map[trip_data["tenant"]]
            driver = driver_map[trip_data["driver"]]
            vehicle = vehicle_map[trip_data["vehicle"]]
            route = route_map[trip_data["route"]]

            trip = Trip(
                key=trip_data["key"],
                tenant_id=tenant.id,
                driver_id=driver.id,
                vehicle_id=vehicle.id,
                route_id=route.id,
                status=trip_data["status"],
                safety_score=trip_data.get("safety_score"),
                score_explanation=trip_data.get("score_explanation"),
            )
            session.add(trip)
        await session.commit()

        print("✅ Database seeded successfully!")
        print(f"   • Tenants:  {len(SEED_DATA['tenants'])}")
        print(f"   • Drivers:  {len(SEED_DATA['drivers'])}")
        print(f"   • Vehicles: {len(SEED_DATA['vehicles'])}")
        print(f"   • Routes:   {len(SEED_DATA['routes'])}")
        print(f"   • Trips:    {len(SEED_DATA['trips'])}")


# ────────────────────────────────────────────────────────────────────────────────
# TELEMETRY EVENT GENERATION
# ────────────────────────────────────────────────────────────────────────────────


async def send_complete_trips(r, event_counter=0):
    """Send 10 complete trips with start, normal_operation, and end_of_trip."""

    trucks = ["TK001", "TK002", "TK003"]
    drivers = ["DRV-ANON-001", "DRV-ANON-002", "DRV-ANON-003", "DRV-ANON-004"]

    base_time = datetime.now(UTC)
    trips_sent = 0

    for trip_num in range(10):
        truck_id = trucks[trip_num % len(trucks)]
        driver_id = drivers[trip_num % len(drivers)]
        trip_id = f"trip-demo-{str(uuid.uuid4())[:8]}"

        trip_duration_minutes = 30 + (trip_num * 10) % 100
        trip_distance_km = 15 + (trip_num * 5) % 80

        trip_start = base_time + timedelta(hours=trip_num)
        start_odometer = 180000 + (trip_num * 100)

        # ─── START OF TRIP
        start_event = {
            "ping_type": "start_of_trip",
            "source": "driver_app",
            "is_emergency": False,
            "event": {
                "event_id": f"evt-start-{trip_num:02d}",
                "device_event_id": f"DEV-START-{trip_num:02d}",
                "trip_id": trip_id,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "event_type": "start_of_trip",
                "category": "trip_lifecycle",
                "priority": "low",
                "timestamp": trip_start.isoformat(),
                "offset_seconds": 0,
                "trip_meter_km": 0.0,
                "odometer_km": float(start_odometer),
                "location": {
                    "lat": 1.2800 + (trip_num * 0.005),
                    "lon": 103.8400 + (trip_num * 0.005),
                },
                "details": {
                    "odometer_km": start_odometer,
                    "fuel_level_litres": 40 + (trip_num % 5),
                    "vehicle_status": "ready",
                },
                "schema_version": "event_v1",
            },
        }
        json_str = json.dumps(start_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1

        # ─── NORMAL OPERATIONS
        normal_event = {
            "ping_type": "batch",
            "source": "telematics_device",
            "is_emergency": False,
            "event": {
                "event_id": f"evt-normal-{trip_num:02d}",
                "device_event_id": f"DEV-NORMAL-{trip_num:02d}",
                "trip_id": trip_id,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "event_type": "normal_operation",
                "category": "normal_operation",
                "priority": "low",
                "timestamp": (
                    trip_start + timedelta(minutes=trip_duration_minutes // 2)
                ).isoformat(),
                "offset_seconds": int((trip_duration_minutes // 2) * 60),
                "trip_meter_km": trip_distance_km / 2,
                "odometer_km": float(start_odometer + int(trip_distance_km / 2)),
                "location": {
                    "lat": 1.2800 + (trip_num * 0.005) + 0.01,
                    "lon": 103.8400 + (trip_num * 0.005) + 0.01,
                },
                "details": {
                    "checkpoint_number": trip_num + 1,
                    "distance_km": trip_distance_km / 2,
                    "speed_avg_kmh": 40 + (trip_num % 20),
                },
                "schema_version": "event_v1",
            },
        }
        json_str = json.dumps(normal_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1

        # ─── END OF TRIP
        end_event = {
            "ping_type": "end_of_trip",
            "source": "driver_app",
            "is_emergency": False,
            "event": {
                "event_id": f"evt-end-{trip_num:02d}",
                "device_event_id": f"DEV-END-{trip_num:02d}",
                "trip_id": trip_id,
                "truck_id": truck_id,
                "driver_id": driver_id,
                "event_type": "end_of_trip",
                "category": "trip_lifecycle",
                "priority": "low",
                "timestamp": (
                    trip_start + timedelta(minutes=trip_duration_minutes)
                ).isoformat(),
                "offset_seconds": trip_duration_minutes * 60,
                "trip_meter_km": trip_distance_km,
                "odometer_km": float(start_odometer + int(trip_distance_km)),
                "location": {
                    "lat": 1.2900 + (trip_num * 0.005),
                    "lon": 103.8500 + (trip_num * 0.005),
                },
                "details": {
                    "duration_minutes": trip_duration_minutes,
                    "distance_km": trip_distance_km,
                    "safety_percentage": 75 + (trip_num % 20),
                },
                "schema_version": "event_v1",
            },
        }
        json_str = json.dumps(end_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1
        trips_sent += 1

    return trips_sent, event_counter


async def send_diverse_events(r, event_counter=0):
    """Send 6 diverse event types to test all agents."""

    DEMO_EVENTS = [
        {
            "name": "harsh_brake",
            "ping_type": "high_speed",
            "source": "telematics_device",
            "event_type": "harsh_brake",
            "priority": "high",
            "details": {"g_force": -0.92, "speed_kmh": 88},
            "count": 2,
        },
        {
            "name": "speeding",
            "ping_type": "medium_speed",
            "source": "telematics_device",
            "event_type": "speeding",
            "priority": "medium",
            "details": {"speed_kmh": 112},
            "count": 1,
        },
        {
            "name": "harsh_corner",
            "ping_type": "high_speed",
            "source": "telematics_device",
            "event_type": "harsh_corner",
            "priority": "high",
            "details": {"g_force_y": 0.87},
            "count": 1,
        },
        {
            "name": "excessive_idle",
            "ping_type": "batch",
            "source": "telematics_device",
            "event_type": "excessive_idle",
            "priority": "low",
            "details": {"idle_duration_seconds": 342},
            "count": 1,
        },
        {
            "name": "driver_sos",
            "ping_type": "emergency",
            "source": "driver_app",
            "event_type": "driver_sos",
            "priority": "critical",
            "details": {"sos_type": "breakdown"},
            "count": 1,
        },
    ]

    total_events = 0
    base_time = datetime.now(UTC)

    for event_config in DEMO_EVENTS:
        for i in range(event_config["count"]):
            test_event = {
                "ping_type": event_config["ping_type"],
                "source": event_config["source"],
                "is_emergency": event_config["priority"] == "critical",
                "event": {
                    "event_id": f"evt-demo-{event_config['name']}-{i:02d}",
                    "device_event_id": f"DEV-{event_config['name'].upper()}-{i:02d}",
                    "trip_id": f"trip-demo-{str(uuid.uuid4())[:8]}",
                    "truck_id": "TK001",
                    "driver_id": f"DRV-DEMO-{i:03d}",
                    "event_type": event_config["event_type"],
                    "priority": event_config["priority"],
                    "timestamp": base_time.isoformat(),
                    "offset_seconds": 120 + (i * 10),
                    "trip_meter_km": 5.4 + (i * 0.5),
                    "odometer_km": 124565.4,
                    "location": {"lat": 1.2863, "lon": 103.8519},
                    "details": event_config["details"],
                    "schema_version": "event_v1",
                },
            }
            json_str = json.dumps(test_event)
            await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
            event_counter += 1
            total_events += 1

    return total_events, event_counter


async def send_random_events(r, event_counter=0, count=20):
    """Send random telemetry events for load testing."""

    events_sent = 0
    base_time = datetime.now(UTC)

    for i in range(count):
        event_type = random.choice(list(EVENT_TYPES_CONFIG.keys()))
        config = EVENT_TYPES_CONFIG[event_type]

        test_event = {
            "ping_type": "batch",
            "source": "telematics_device",
            "is_emergency": config["priority"] == "critical",
            "event": {
                "event_id": f"evt-random-{event_type}-{i:03d}",
                "device_event_id": f"DEV-RAND-{i:03d}",
                "trip_id": random.choice(TRIP_IDS),
                "truck_id": random.choice(TRUCK_IDS),
                "driver_id": random.choice(DRIVER_IDS),
                "event_type": event_type,
                "category": config["category"],
                "priority": config["priority"],
                "timestamp": base_time.isoformat(),
                "offset_seconds": random.randint(0, 3600),
                "trip_meter_km": round(random.uniform(0.1, 50.0), 1),
                "odometer_km": round(random.uniform(100000, 200000), 1),
                "location": random.choice(LOCATIONS),
                "details": config["details"],
                "schema_version": "event_v1",
            },
        }

        json_str = json.dumps(test_event)
        await r.zadd("telemetry:TK001:buffer", {json_str: event_counter})
        event_counter += 1
        events_sent += 1

    return events_sent, event_counter


# ────────────────────────────────────────────────────────────────────────────────
# MAIN HANDLER
# ────────────────────────────────────────────────────────────────────────────────


async def send_telemetry(mode="all"):
    """Send telemetry data or seed database based on mode."""

    # Handle database seeding
    if mode in ("db", "all"):
        print("🌱 Seeding database...")
        try:
            await seed_database()
        except Exception as e:
            print(f"⚠️  Database seeding warning: {e}")

    # Handle Redis telemetry
    if mode in ("trips", "diverse", "random", "all"):
        r = await redis.from_url("redis://localhost:6379/0")

        try:
            await r.delete("telemetry:TK001:buffer")

            event_counter = 0
            trips_sent = 0
            diverse_events = 0
            random_events = 0

            if mode in ("trips", "all"):
                print("📤 Sending complete realistic trips...")
                trips_sent, event_counter = await send_complete_trips(r, event_counter)

            if mode in ("diverse", "all"):
                print("📤 Sending diverse event types for agent testing...")
                diverse_events, event_counter = await send_diverse_events(
                    r, event_counter
                )

            if mode in ("random", "all"):
                print("📤 Sending random telemetry events...")
                random_events, event_counter = await send_random_events(
                    r, event_counter, count=20
                )

            print("\n" + "=" * 60)
            print("✅ TELEMETRY DATA SENT TO REDIS")
            print("=" * 60)
            print(f"Queue:           telemetry:TK001:buffer")
            print(f"Total events:    {event_counter}")

            if trips_sent > 0:
                print(f"\n📊 COMPLETE TRIPS:")
                print(f"   • Trips sent:           {trips_sent}")
                print(f"   • Events per trip:      3 (start, normal_op, end)")

            if diverse_events > 0:
                print(f"\n🎯 DIVERSE EVENTS:")
                print(f"   • harsh_brake:          ×2 → Safety agent")
                print(f"   • harsh_corner:         ×1 → Safety agent")
                print(f"   • driver_sos:           ×1 → Safety agent")
                print(f"   • speeding:             ×1 → Support agent")
                print(f"   • excessive_idle:       ×1 → Support agent")

            if random_events > 0:
                print(f"\n🎲 RANDOM EVENTS:")
                print(f"   • Total random events:  {random_events}")

            print(f"\n✅ Queue size: {event_counter} events ready for processing")
            print("=" * 60)

        finally:
            await r.aclose()


def main():
    mode = "all"

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        valid_modes = ("db", "trips", "diverse", "random", "all")
        if arg not in valid_modes:
            print("Usage: python send_telemetry.py [mode]")
            print("\nModes:")
            print("  db      - Seed database with drivers, vehicles, routes, trips")
            print("  trips   - Send 10 complete realistic trips")
            print("  diverse - Send 6 diverse event types (agent routing test)")
            print("  random  - Send 20 random telemetry events (load test)")
            print("  all     - All of the above (default)")
            sys.exit(1)
        mode = arg

    asyncio.run(send_telemetry(mode))


if __name__ == "__main__":
    main()
