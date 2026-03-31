# TraceData AI Monorepo

Real-time telemetry pipeline for fleet vehicle safety monitoring. Processes driver and vehicle events through distributed AI agents.

## Quick Start (5 minutes)

### Prerequisites
- **Docker & Docker Compose** ([Install here](https://docs.docker.com/get-docker/))
- **Git** for version control

### Step 1: Clone and navigate
```bash
git clone <repo-url>
cd tracedata-ai-monorepo
```

### Step 2: Start all services
```bash
docker compose up -d
```

Wait ~30 seconds for services to boot. Check status:
```bash
docker compose ps
```

You should see 10 services running (api, ingestion, orchestrator, safety_worker, etc.)

### Step 3: Initialize the database
```bash
docker compose exec -T api python -m scripts.setup_db
```

This creates the `pipeline_events` and `pipeline_trips` tables.

### Step 4: Seed test data
```bash
docker compose exec -T api python -m scripts.seed_telemetry_batch --count 50
```

This generates 50 sample telemetry events (collisions, harsh braking, driver SOS, etc.)

### Step 5: Verify the pipeline is working
```bash
# Check events in database (should see ~33 processed)
docker compose exec -T db psql -U postgres -d tracedata -c "SELECT COUNT(*) FROM pipeline_events;"

# Check orchestrator dispatching to agents
docker compose logs orchestrator | grep dispatch | head -5
```

**Expected output:** Events flowing through orchestrator → Safety/Sentiment/Scoring agents

### Step 6: View live API
```bash
# API is available at http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

---

## System Architecture

```
Device Telemetry (Redis Buffer)
    ↓
Ingestion Sidecar (validates & stores)
    ↓
PostgreSQL Database (pipeline_events)
    ↓
Orchestrator (acquires locks, routes events)
    ↓
Agent Workers (Safety, Sentiment, Scoring, Support)
    ↓
Results → Redis Cache & Webhooks
```

## Available Services

| Service | Purpose | Port |
|---------|---------|------|
| **api** | FastAPI REST endpoints | 8000 |
| **ingestion** | Telemetry processing sidecar | - |
| **orchestrator** | Event dispatch orchestration | - |
| **safety_worker** | Safety incident analysis | - |
| **sentiment_worker** | Driver sentiment analysis | - |
| **scoring_worker** | Safety scoring | - |
| **support_worker** | Support escalation logic | - |
| **db** | PostgreSQL database | 5432 |
| **redis** | Queue & cache store | 6379 |
| **frontend** | Next.js dashboard | 3000 |

## Common Commands

```bash
# View logs
docker compose logs orchestrator -f          # Follow orchestrator
docker compose logs safety_worker --tail 50  # Last 50 lines of safety agent

# Stable sentiment-agent trigger (inject driver feedback event)
docker compose exec -T api python -m scripts.seed_sentiment_event --count 1 --event-type driver_feedback

# Reset everything
docker compose down -v    # Remove containers and volumes
docker system prune -f    # Clean up unused images
docker compose up -d      # Start fresh

# Access database
docker compose exec -T db psql -U postgres -d tracedata

# Check Redis queues
docker compose exec -T redis redis-cli KEYS "buffer:*" COUNT 10
```

## Documentation
- [Architecture & Design](docs/01-project-documents/TDATA-49-architecture.md)
- [Git Workflow](docs/02-guides/02-git-workflow.md)
- [Troubleshooting](docs/02-guides/10_troubleshooting_guide.md)
- [Agent Details](docs/03-agents/)
