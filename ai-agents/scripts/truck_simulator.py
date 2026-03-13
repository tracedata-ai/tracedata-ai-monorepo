import asyncio
import json
import random
import uuid
import time
import os
from aiokafka import AIOKafkaProducer

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle.telemetry")

async def simulate_trucks():
    """
    Simulates telemetry data from multiple trucks and publishes it to Kafka.
    """
    print(f"Simulator: Connecting to Kafka at {KAFKA_BOOTSTRAP_SERVERS}...")
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    await producer.start()
    print("Simulator: Started. Press Ctrl+C to stop.")

    trucks = [
        {"id": "TRUCK-001", "driver": "Wei Ming Tan"},
        {"id": "TRUCK-002", "driver": "Siti Aisha"},
        {"id": "TRUCK-003", "driver": "Rajan Sivan"},
    ]

    try:
        while True:
            for truck in trucks:
                event = {
                    "event_id": str(uuid.uuid4()),
                    "event_type": random.choice(["telemetry", "location_update", "ping"]),
                    "vehicle_id": truck["id"],
                    "driver_id": truck["driver"],
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "details": {
                        "fuel_level": random.randint(10, 100),
                        "tire_pressure": random.randint(30, 45),
                        "speed": random.randint(0, 90),
                        "lat": 1.3521 + random.uniform(-0.1, 0.1),
                        "lng": 103.8198 + random.uniform(-0.1, 0.1)
                    }
                }
                
                print(f"Simulator: Sending event for {truck['id']}...")
                await producer.send_and_wait(KAFKA_TOPIC, event)
                await asyncio.sleep(random.uniform(1, 4))
                
    except Exception as e:
        print(f"Simulator error: {e}")
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(simulate_trucks())
