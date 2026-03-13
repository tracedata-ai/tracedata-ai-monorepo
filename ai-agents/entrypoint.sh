#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting TraceData AI Middleware..."

# Set PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:.

# Automated Seeding for the web service
echo "Running database initialization and seeding..."
python scripts/seed_data.py

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
