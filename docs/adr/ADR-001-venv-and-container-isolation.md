# ADR-001: Virtual Environment and Container Isolation Strategy

**Date:** 2026-03-19
**Status:** Accepted
**Deciders:** Backend Team

## Context

TraceData is a Python monorepo containing multiple services:

- `backend/` — FastAPI REST API + 5 AI agents (co-located)
- `frontend/` — Next.js dashboard

During initial setup, a `.venv` was created at the **monorepo root** (inherited from an earlier project layout). Simultaneously, questions arose about whether each AI agent (Orchestrator, Ingestion, Behavior, Feedback, Safety) should have its own isolated Python virtual environment.

Two decisions needed to be made:

1. Where should virtual environments live?
2. Should individual agents have their own venvs?

## Decision

### 1. One venv per container image (not per agent, not per monorepo root)

Each `Dockerfile` produces exactly one container image. That image contains exactly one virtual environment, installed from **one `pyproject.toml`** in that service's directory.

```
backend/
├── pyproject.toml   ← one manifest
├── uv.lock          ← one lockfile
└── .venv/           ← one venv (created by `uv sync` inside backend/)
```

**The root-level `.venv` was deleted.** Nothing should import from the monorepo root.

### 2. Agents remain co-located in the `backend/` container (for now)

All agents live as subpackages under `backend/agents/`. They share the backend container, the backend venv, and the backend `pyproject.toml`.

```
backend/agents/
├── orchestrator/   ← importable as app.agents.orchestrator
├── ingestion/
├── behavior/
├── feedback/
└── safety/
```

---

## Rationale

### Why NOT one venv per agent?

A virtual environment exists to isolate Python package installations from one another within **a single machine or process**. Docker containers are already isolated processes with their own filesystems. Running multiple venvs inside one container adds complexity with no benefit — Python can only use one venv at a time per process anyway.

```
Container filesystem IS the isolation boundary.
venv = isolation within a single OS environment (no Docker).
```

### Why NOT one venv at the monorepo root?

> **Important distinction:** agents sharing `backend/.venv` is **intentional and correct** —
> they are co-located in one Python process and can only use one venv anyway.
> The problem here is a **root-level** venv that tries to serve every service at once.

The original project had a `.venv` at the repo root, created by running Python commands without
a proper project structure. This is wrong because:

- **Service boundary pollution** — `backend/` Python deps (FastAPI, asyncpg, LangGraph) get
  mixed with any future root-level tooling (CI scripts, Alembic migration runners). There is
  no clean line between what belongs to which service.
- **Docker ambiguity** — With a root `pyproject.toml`, `uv sync` from any subdirectory may
  resolve upward to the root, producing unpredictable installs in the container.
- **Future image bloat** — When the Behavior Agent eventually needs `xgboost` + `aif360`
  (~600 MB), those land in the root venv and get pulled into every image unnecessarily.

### Why co-locate agents in the backend container?

| Factor                 | Co-located                     | Separate containers                            |
| ---------------------- | ------------------------------ | ---------------------------------------------- |
| Inter-agent calls      | Direct function calls (0ms)    | HTTP / message queue (latency + serialisation) |
| Shared DB pool         | Yes — one pool, reused         | No — each container opens its own connections  |
| Operational complexity | Low — one container to monitor | High — N containers, N health checks, N logs   |
| Independent scaling    | No                             | Yes                                            |
| Independent deployment | No                             | Yes                                            |
| Capstone suitability   | High                           | Over-engineered for scope                      |


The primary driver: **agents need to share the same database session and configuration at zero latency**. For a capstone project, the operational overhead of separate containers per agent is not justified.

## Consequences

- **Developer workflow:** Run `uv sync` from `backend/` — always, never from the monorepo root.
- **Docker:** Each `Dockerfile.*` in `backend/` installs its own clean venv via `uv sync --no-dev`.
- **Extraction path:** If an agent must be extracted (e.g., Behavior Agent for GPU-accelerated scoring), it gets its own `pyproject.toml` under `backend/agents/behavior/` and a new `Dockerfile.behavior`. The code structure already supports this — no refactoring needed.
- **uv workspaces:** When the first agent is extracted, migrate to [uv workspaces](https://docs.astral.sh/uv/concepts/workspaces/) to maintain a single shared lockfile across all service `pyproject.toml` files.

## Rejected Alternatives

| Alternative                                | Why rejected                                                                       |
| ------------------------------------------ | ---------------------------------------------------------------------------------- |
| One root venv for all services             | Dependency conflicts; bloated Docker images                                        |
| One venv per agent (inside same container) | A process can only activate one venv; adds no isolation benefit inside a container |
| Separate container per agent immediately   | Over-engineered for capstone scope; high operational overhead                      |

_This ADR should be revisited if:_

- _Any agent requires a conflicting dependency version_
- _Any agent's Docker image exceeds 1 GB due to heavy ML libraries_
- _Independent agent scaling becomes a requirement_
