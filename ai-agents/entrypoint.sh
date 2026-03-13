#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting TraceData AI Middleware Entrypoint..."

# Determine service type to run
SERVICE_TYPE=${SERVICE_TYPE:-api}

echo "Service Role: $SERVICE_TYPE"

if [ "$SERVICE_TYPE" = "api" ]; then
    # Automated Seeding for the web service
    echo "Running database initialization and seeding..."
    uv run python scripts/seed_data.py
    
    echo "Starting FastAPI application..."
    exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
    
elif [ "$SERVICE_TYPE" = "worker" ]; then
    echo "Starting Celery Worker..."
    # -A app.core.celery_app specifies the celery instance
    exec celery -A app.core.celery_app worker --loglevel=info
    
elif [ "$SERVICE_TYPE" = "consumer" ]; then
    echo "Starting Kafka Telemetry Consumer..."
    exec python -m app.services.kafka_consumer
    
else
    echo "Unknown SERVICE_TYPE: $SERVICE_TYPE"
    exit 1
fi
