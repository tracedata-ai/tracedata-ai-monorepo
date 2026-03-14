#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting TraceData AI Middleware..."

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:.

# Automated Seeding for the web service (Optional: Only if requested or on first run)
if [ "$RUN_SEEDER" = "true" ]; then
    echo "Running database initialization and seeding..."
    python scripts/seed_data.py
fi

# If no command is provided, default to starting FastAPI
if [ $# -eq 0 ]; then
    echo "Starting FastAPI application..."
    exec uvicorn main:app --host 0.0.0.0 --port 8000
else
    echo "Executing command: $@"
    exec "$@"
fi
