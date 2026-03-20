# ADR-002: Consolidated 'core' Package for Cross-Cutting Infrastructure

**Date:** 2026-03-20
**Status:** Accepted
**Deciders:** TraceData Architecture Team

---

## Context

The TraceData backend is a **Modular Monolith** that hosts two distinct workload types:
1.  **FastAPI REST API** (`app/`): Handles user requests and fleet management.
2.  **AI Agent Service** (`agents/`): Orchestrates LangGraph-based telemetry analysis.

Originally, cross-cutting concerns (Database session management, Pydantic settings, and Logging configuration) were located within `backend/app/core/`. This created a dependency bottleneck: if the `agents/` layer needed to access the database or settings, it had to import from the `app/` package, violating the principle of independent service layers and making future microservice extraction difficult.

---

## Decision

**Extract all shared infrastructure into a top-level `core/` package.**

The new package structure:
```text
backend/
├── app/    # Application Logic (REST)
├── agents/ # AI Agent Logic
└── core/   # SHARED PLUMBING (Config, DB, Logging)
```

### Dependency Structure (MermaidJS)

```mermaid
graph TD
    subgraph "Backend"
        core["Core Infrastructure (Shared)"]
        app["FastAPI Application (Service)"]
        agents["AI Agent Service (Service)"]
    end

    db[("PostgreSQL")]

    app ..> core
    agents ..> core
    core ..> db
```

---

## Rationale

### Why a shared top-level `core`?

| Factor | App-Scoped Core (`app/core`) | Shared Top-Level Core (`core/`) |
| :--- | :--- | :--- |
| **Coupling** | High. Agents depend on App layer. | Low. Both layers depend on a common utility layer. |
| **Scalability** | Hard. Difficult to separate Agents into their own Docker image. | Easy. Agents can be deployed solo with just the `core` package. |
| **Namespace** | `from app.core import ...` | `from core import ...` |
| **Standardization** | Inconsistent (scripts used `basicConfig`). | Unified (scripts and services use `core.logging`). |

---

## Consequences

-   ✅ **Service Independence**: Agents can now be moved to a separate repository or container without carrying any FastAPI code.
-   ✅ **Typed Observability**: All modules (including standalone CLI tools) now share the `LogToken` Enum for consistent monitoring.
-   ✅ **Simplified Imports**: Core utilities are exactly one level deep (`from core.database import engine`).
-   ⚠️ **Refactor Effort**: Required updating ~30 import statements across 12+ files.
-   ⚠️ **Build Config**: Required updating `pyproject.toml` to include the `core` package in the build target.

---

## References

- [Architecture Overview](../01-project-documents/TDATA-49-architecture.md)
- [TDATA-49 Branch History](https://github.com/tracedata-ai/tracedata-ai-monorepo/pull/49)
