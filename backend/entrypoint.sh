#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
# TraceData Backend — Container Entrypoint
#
# This script runs inside the Docker container before starting uvicorn.
# It handles two responsibilities:
#   1. Wait for PostgreSQL to be ready (avoids "connection refused" on startup)
#   2. Optionally seed the database (controlled by RESET_DB env var)
# ─────────────────────────────────────────────────────────────────────────────

set -e  # Exit immediately on any error

echo "⏳ Waiting for PostgreSQL..."

# Simple TCP port check — retries until DB is accepting connections.
# In production, replace with `pg_isready` for a proper readiness check.
until python -c "
import asyncio, asyncpg, os
async def check():
    url = os.environ.get('DATABASE_URL', '').replace('postgresql+asyncpg://', '')
    await asyncpg.connect(dsn='postgresql://' + url)
asyncio.run(check())
" 2>/dev/null; do
  echo "  DB not ready — retrying in 2s..."
  sleep 2
done

echo "✅ PostgreSQL is ready."

# ── Seeding (Nuke & Pave) ─────────────────────────────────────────────────────
if [ "${RESET_DB}" = "true" ]; then
  echo "🔄 RESET_DB=true — running seed script..."
  python -m scripts.seed
  echo "✅ Database seeded."
else
  echo "⏭️  RESET_DB=false — skipping seed."
fi

# ── Baseline data bootstrap (idempotent) ──────────────────────────────────────
python -m scripts.bootstrap_sg_baseline

# ── Start Celery Beat scheduler (background) ──────────────────────────────────
# Beat runs alongside uvicorn inside the same container — mirrors docker-compose.
# Routes watchdog tasks to the safety worker queue (td:agent:safety).
echo "🕐 Starting Celery Beat scheduler (background)..."
celery -A celery_app beat --loglevel=info &

# ── Start Server ──────────────────────────────────────────────────────────────
echo "🚀 Starting TraceData Backend..."
exec uvicorn api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 1 \
  --log-level info
