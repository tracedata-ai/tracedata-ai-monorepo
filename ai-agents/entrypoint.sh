#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "Starting TraceData AI Middleware Entrypoint..."

# Automated Seeding
# This script is idempotent (if RESET_DB is false)
# or destructive (if RESET_DB is true)
echo "Running database initialization and seeding..."
uv run python scripts/seed_data.py

echo "Database ready. Starting FastAPI application..."

# Start the application using uv run to ensure the virtualenv is used
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
