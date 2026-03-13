import asyncio
import json
import random
import uuid
import time
import os
from aiokafka import AIOKafkaProducer
from app.core.logging import setup_logging, get_logger

# Initialize logging
setup_logging()
logger = get_logger("scripts.truck_simulator")

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle.telemetry")

async def simulate_trucks():
    """
    Simulates telemetry data from multiple trucks and publishes it to Kafka.
    """
    logger.info("Connecting to Kafka", broker=KAFKA_BOOTSTRAP_SERVERS)
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    await producer.start()
    logger.info("Simulator started. Press Ctrl+C to stop.")

    trucks = [
        {"id": "TRUCK-001", "driver": "Wei Ming Tan"},
        {"id": "TRUCK-002", "driver": "Siti Aisha"},
        {"id": "TRUCK-003", "driver": "Rajan Sivan"},
    ]

    try:
        while True:
            for truck in trucks:
                # Use formal taxonomy from SRS 3.3.2
                event_type = random.choice([
                    "collision", "rollover", "harsh_brake", 
                    "hard_accel", "harsh_corner", "speeding", 
                    "excessive_idle", "normal_operation"
                ])
                
                category_map = {
                    "collision": "critical",
                    "rollover": "critical",
                    "harsh_brake": "harsh_event",
                    "hard_accel": "harsh_event",
                    "harsh_corner": "harsh_event",
                    "speeding": "speed_compliance",
                    "excessive_idle": "idle_fuel",
                    "normal_operation": "normal_operation"
                }

                priority_map = {
                    "collision": "critical",
                    "rollover": "critical",
                    "harsh_brake": "high",
                    "hard_accel": "high",
                    "harsh_corner": "high",
                    "speeding": "medium",
                    "excessive_idle": "low",
                    "normal_operation": "low"
                }

                event = {
                    "event_id": str(uuid.uuid4()),
                    "event_type": event_type,
                    "category": category_map[event_type],
                    "priority": priority_map[event_type],
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
                
                logger.info("Sending telemetry event", 
                            event_type=event_type, 
                            vehicle_id=truck['id'],
                            priority=priority_map[event_type])
                await producer.send_and_wait(KAFKA_TOPIC, event)
                await asyncio.sleep(random.uniform(1, 4))
                
    except Exception as e:
        logger.error("Simulator execution error", error=str(e), exc_info=True)
    finally:
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(simulate_trucks())
