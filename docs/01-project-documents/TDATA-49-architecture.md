# TDATA-49: Backend Foundation & Architecture Overview

**Branch:** `develop/TDATA-49-Backend-API-and-Agent-folder-setup`
**Status:** Locked & Documented

---

## 1. Problem Statement

The platform required a robust foundation to support high-volume telematics and multi-agent coordination. The primary challenge was designing a structure that allowed the **REST API** and **AI Agents** to coexist while sharing critical infrastructure without tight coupling.

## 2. Theoretical Background: Modular Monolith

We chose a **Modular Monolith** to maintain ACID transactions across the Fleet and Booking modules during the MVP phase, while using **Schema-per-Module** database design to ensure future microservice readiness.

---

## 3. Architecture Overview (MermaidJS)

```mermaid
graph TD
    subgraph "Backend Monorepo"
        app["FastAPI App (Service)"]
        agents["AI Agents (Service)"]
        core["Core Utils (Infrastructure)"]
    end

    subgraph "PostgreSQL"
        fleet_schema[("Schema: Fleet")]
        trips_schema[("Schema: Trips")]
    end

    app --> core
    agents --> core
    core --> fleet_schema
    core --> trips_schema
```

---

## 4. Design Standards & Accomplishments

### A. Observability (Typed Log Tokens)

We standardized all logging to use machine-parsable tokens. This ensures that automated monitoring (Datadog/ELK) can parse events with 100% reliability.

**Standard Tokens Reference:**

- `[STARTUP]` - System initialization
- `[DATABASE_INIT]` - Database schema verification
- `[SEED_SUCCESS]` - Data population completed
- `[FAIL]` - Retriable failure
- `[ERROR]` - Critical system failure

### B. Tactical DDD Patterns

- **`UUIDPrimaryKeyMixin`**: Guarantees non-sequential, globally unique IDs for all entities.
- **`TimestampMixin`**: Provides automated audit trails for every row creation and update.
- **`get_db()`**: Injected dependency that automatically manages transaction lifecycles (commit on success, rollback on error).

### C. Multi-Tenant Isolation Strategy

- **Logical Partitioning**: Every domain model (Vehicle, Driver, Trip, Issue) contains a `tenant_id` (UUID).
- **No Foreign Keys across Schemas**: While we use a single database, cross-module references use UUIDs instead of hard Foreign Keys. This follows the **Modular Monolith** principle, allowing us to split the database into separate RDS instances for each module in the future without code changes.

### D. Correlation Tracing & Reliability

- **`X-Request-ID` Propagation**: Every log line is tagged with a `request_id` via `ContextVars`. This allows us to trace a single user request across Middleware -> FastAPI -> SQLAlchemy logs.
- **Circuit Breaker Readiness**: The typed logging of `[FAIL]` and `[ERROR]` is designed to trigger automated circuit breakers and retry logic in our future API Gateways.

### E. Sequence Flow: Request Lifecycle (MermaidJS)

```mermaid
sequenceDiagram
    participant User as Client/Frontend
    participant MW as Middleware (RequestId)
    participant API as FastAPI Router
    participant DB as Postgres (SQLAlchemy)
    participant Log as LogSystem (Observability)

    User->>MW: GET /api/v1/fleet (X-Request-ID)
    MW->>MW: Assign RequestID (ContextVar)
    MW->>API: Dispatch Request
    API->>Log: LogToken.STARTUP
    API->>DB: async select()
    DB-->>API: Result set
    API->>Log: LogToken.SUCCESS
    API-->>User: JSON + X-Request-ID
```

---

## 6. Project References

- [Caching Strategy](./10-caching-strategy.md)
- [ADR-003: Shared Core Package](../adr/ADR-003-shared-core-package.md)
- [ADR-002: Messaging Layer](../adr/ADR-002-kafka-to-redis-celery.md)
- [ADR-001: Environment Isolation](../adr/ADR-001-venv-and-container-isolation.md)
