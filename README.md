# TraceData AI Monorepo

Real-time fleet telemetry → PostgreSQL → orchestrator → Celery agent workers (Safety, Sentiment, Scoring, Support), backed by Redis for buffers, queues, and trip context.

## Quick Start

**Requires:** Docker Compose, Git.

```bash
git clone <repo-url> && cd tracedata-ai-monorepo
docker compose up -d
docker compose exec -T api python -m scripts.setup_db
docker compose exec -T api python -m scripts.seed_telemetry_batch --count 50
```

- **API / docs:** http://localhost:8000 and http://localhost:8000/docs  
- **Sanity:** `docker compose exec -T db psql -U postgres -d tracedata -c "SELECT COUNT(*) FROM pipeline_events;"`  
- Expect ~10 containers (api, ingestion, orchestrator, workers, db, redis, frontend).

---

## Architecture (diagrams)

### 1. Stack (Docker Compose)

Celery broker and backend share **the same Redis** as telemetry and trip keys (see `docker-compose.yml`).

```mermaid
flowchart TB
  subgraph clients [Clients]
    FE[frontend:3000]
    DEV[Devices]
  end
  subgraph stores [Stores]
    PG[(Postgres:5432)]
    RD[(Redis:6379)]
  end
  subgraph procs [Backend]
    API[api]
    ING[ingestion]
    ORC[orchestrator]
    SAF[safety_worker]
    SCO[scoring_worker]
    SUP[support_worker]
    SEN[sentiment_worker]
  end
  FE --> API
  DEV -->|telemetry buffer| RD
  API --> PG
  API --> RD
  ING --> RD
  ING --> PG
  ORC --> RD
  ORC --> PG
  SAF --> RD
  SCO --> RD
  SCO --> PG
  SUP --> RD
  SEN --> RD
  ORC -->|Celery| RD
```

### 2. Data and dispatch pipeline

Buffers and **processed** queues are Redis **sorted sets**. Orchestrator **polls** processed ZSETs, acquires DB lease, routes via LLM + EventMatrix, **warms** `trips:{trip_id}:{agent}:*`, **send_task** to `td:agent:*`. Workers write `trip:{trip_id}:{agent}_output` and publish completions on `trip:{trip_id}:events`.

```mermaid
flowchart TB
  DEV[Telemetry] --> BUF[telemetry:truck:buffer ZSET]
  BUF --> ING[Ingestion plus sidecar]
  ING --> PG[(pipeline_events)]
  ING --> PROC[telemetry:truck:processed ZSET]
  PROC --> ORC[Orchestrator poll]
  ORC --> RTE[Route warm capsule]
  RTE --> CEL[Celery broker]
  CEL --> W[Agent workers]
  W --> OUT["trip:trip_id:agent_output"]
  W --> EVT["trip:trip_id:events"]
  SCO[scoring_worker] -->|coaching_ready if pending| PROC
```

### 3. Post-trip coaching handoff (`coaching_ready`)

On **`end_of_trip`**, support is **not** dispatched in that wave; after scoring, **`schedule_coaching_ready_if_pending`** may push **`coaching_ready`** back onto the truck’s **processed** queue so **support_worker** runs with post-scoring context. **`sentiment_ready`** behaves similarly after sentiment.

```mermaid
sequenceDiagram
  participant O as Orchestrator
  participant Z as processed ZSET
  participant S as scoring_worker
  participant R as trip context Redis
  participant P as support_worker
  O->>Z: pop end_of_trip
  O->>S: score_trip
  S->>R: update context
  S->>Z: enqueue coaching_ready when pending
  O->>Z: pop coaching_ready
  O->>P: generate_coaching
```

---

## Runtime checklist (short)

1. `telemetry:{truck_id}:buffer` ← raw; ingestion → `pipeline_events` + `telemetry:{truck_id}:processed`.
2. Orchestrator: lock → route → warm → Celery.
3. Workers: capsule reads; writes `*_output`; `trip:{trip_id}:events` completions.
4. Follow-ups: `sentiment_ready` / `coaching_ready` → support when applicable.
5. `trip:{trip_id}:context` holds rolling flags and latest agent summaries.

| Component | Reads (summary) | Writes (summary) |
|-----------|-----------------|------------------|
| ingestion | buffer ZSET | processed ZSET, `pipeline_events` |
| orchestrator | processed, `trip:events`, DB | Celery `td:agent:*`, warmed keys, `trip:context` |
| workers | queues + scoped trip keys | `trip:*_output`, schema tables, completions |

Full matrix: see [TDATA-49-architecture](docs/01-project-documents/TDATA-49-architecture.md) or agent docs below.

| Service | Port |
|---------|------|
| api | 8000 |
| frontend | 3000 |
| db | 5432 |
| redis | 6379 |
| ingestion, orchestrator, safety/scoring/support/sentiment workers | internal |

## Common commands

```bash
docker compose logs orchestrator -f
docker compose exec -T db psql -U postgres -d tracedata
docker compose exec -T redis redis-cli SCAN 0 MATCH "telemetry:*:buffer" COUNT 100
```

## Documentation

- [Architecture & Design](docs/01-project-documents/TDATA-49-architecture.md)
- [Git Workflow](docs/02-guides/02-git-workflow.md)
- [Troubleshooting](docs/02-guides/10_troubleshooting_guide.md)
- [Agent Details](docs/03-agents/)
