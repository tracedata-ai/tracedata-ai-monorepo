# TraceData Architecture Constraints

This module defines the core stack, data pipelines, and architectural boundaries for the TraceData project.

## Core Stack

- **Backend**: Python (FastAPI + LangGraph) — Agentic AI Middleware Monolith
- **Frontend**: **Next.js 16 (App Router)**
- **Styling**: **Tailwind CSS v4** + **Shadcn UI**
- **Language**: **TypeScript 5** (Strict mode)
- **Data Logic**: **TanStack Table (v8)** for data-heavy views, **Recharts** for telemetry charts
- **Database**: PostgreSQL with pgvector (semantic search)
- **Messaging**: WebSocket (real-time safety alerts)

## Backend Service Isolation (Python)

The Agentic AI Middleware follows a strict **package-first modular monolith** structure:

- **Root Directory**: `backend/` (Contains build/CI config: `Dockerfile`, `requirements.txt`, `.github/`)
- **App Package**: `backend/app/` (The core executable package)
- **Service Entry**: Always exposed via `app.main:app` for production-grade imports and containerization.
- **Shared Modules**: Internal logic split into `agents/`, `api/`, `models/`, `schemas/`, and `services/`.

## Multi-Tenancy (MANDATORY)

Every data layer must include and enforce `tenant_id`:

- **Telematics Data**: GPS, speed, RPM pings tagged with tenant
- **Driver Profiles**: Isolated per tenant
- **Trip Logs**: Segregated by tenant_id
- **Frontend Data Flow**: Verify `tenant_id` on every API call; never process data without it

**In API routes:**

```typescript
// src/pages/api/drivers.ts
const tenantId = req.headers["x-tenant-id"] || getUserTenant(token);
if (!tenantId)
  return res.status(403).json({ error: "Tenant context required" });
// Query with WHERE tenant_id = tenantId
```

## Ingestion & Data Pipelines

### Telematics (Direct Ingestion)

TraceData uses a **Direct Persistence & Agentic Reasoning** model for telemetry:

1.  **Ingestion (FastAPI)**:
    - Telemetry from vehicles is POSTed directly to the `/api/v1/telemetry` endpoint.
2.  **Persistence (PostgreSQL)**:
    - The middleware immediately persists the raw event to the `telemetry_events` table for traceability.
3.  **In-Process Reasoning (LangGraph)**:
    - The event is passed directly to the Agentic Shell Orchestrator.
    - Reasoning (anomaly detection, coaching triggers) happens within the request lifecycle or as an internal async task.
4.  **System of Record**:
    - Final enriched state and safety alerts are committed to the DB.

**Ping Types:**

- `Emergency Ping` — Critical events (accidents, extreme braking)
- `Normal Ping` — Standard telemetry (GPS, Speed, Fuel)
- `Start/End of Trip` — Handled via state transitions in the Trip module

### Unstructured Driver Input

- **Source**: Driver app (free-text reviews, feedback, formal appeals)
- **Routing**: Goes through Ingestion Quality Agent
- **Storage**: PostgreSQL with pgvector for semantic search

### Frontend Integration

- Never assume data is immediately available; handle async loading states
- Telematics batches arrive every 4–10 minutes; refresh metrics accordingly
- Safety-critical alerts come via WebSocket from Kafka; display immediately with sub-500ms latency

## Context Enrichment (MCP)

- **Input**: Raw GPS coordinates, timestamps
- **Output**: Rich geographic data (Place Name, Topology, Weather, Traffic)
- **Tool Service**: Returns in < 2 seconds; used by Behavior, Safety, Orchestrator agents
- **Frontend Use**: Display location context and weather conditions in trip details, driver profiles

## Safety Intervention (Multi-Level)

Evaluated by Safety Agent on Critical Events:

- **Level 1 (Minor)**: App notification / in-cab reminder
- **Level 2 (Moderate)**: Formal message logged and sent to driver
- **Level 3 (Serious)**: Escalation/call to Fleet Manager

**Frontend**: Display safety levels with corresponding urgency (red for Level 3, orange for Level 2, yellow for Level 1)

## Driver Encouragement & Profiling

- **Objective**: The system must go beyond penalization to build an encouragement profile. Raw telemetry points must be aggregated to detect positive driving patterns.
- **Reasoning**: The AI (Orchestrator or Coaching Agent) uses these aggregated data points and contextual anomalies to reason autonomously, deciding when to boost encouragement scores.

## Internal State & Persistence

- **PostgreSQL (`pgvector`)**: Mandatory for semantic search against historical profiles and text submissions.
- **Table Segregation**: Each processing agent writes its outputs to distinct tables, correlated by `trip_id` and isolated by `tenant_id`.

## AI Security & Guardrails

- **LLM Rate Limiting**: Strict per-driver/per-tenant token quotas
- **Prompt Sanitization**: Explicit templating; sanitize all user input before passing to agents
- **Fairness Monitoring**: Track Statistical Parity Difference (SPD); alert if drift > 0.2
- **Data Privacy**: RBAC (JWT) for auth, AES-256 encryption for driver feedback
