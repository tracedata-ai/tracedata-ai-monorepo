import asyncio
import json
import os
from aiokafka import AIOKafkaConsumer
from app.services.tasks import process_telemetry_event

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "vehicle.telemetry")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "tracedata-consumer-group")

async def consume_telemetry():
    """
    Asynchronous Kafka consumer that listens for telemetry events.
    When a message is received, it dispatches it to Celery for processing.
    """
    print(f"Kafka: Connecting to {KAFKA_BOOTSTRAP_SERVERS}...")
    
    # Initialize the consumer
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    try:
        # Get cluster layout and join group
        await consumer.start()
        print(f"Kafka: Consumer started. Listening on topic '{KAFKA_TOPIC}'...")

        async for msg in consumer:
            payload = msg.value
            print(f"Kafka: Received event {payload.get('event_id')} from topic {msg.topic}")
            
            # Dispatch to Celery (hand-off)
            process_telemetry_event.delay(payload)
            
    except Exception as e:
        print(f"Kafka: Consumer error: {e}")
    finally:
        # Will leave consumer group; perform clean shutdown
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume_telemetry())
