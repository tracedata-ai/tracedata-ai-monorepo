# ADR 002: uv Workspaces for Monorepo Dependency Management

## Status
Accepted

## Context
TraceData is a monorepo containing multiple Python services and scripts. Managing dependencies across these services efficiently, ensuring lockfile consistency, and maintaining fast CI/CD pipelines are critical requirements. Traditional tools like `pip` (standard) or `poetry` (feature-rich but slower/complex in monorepos) were considered.

## Decision
We have chosen **uv (by Astral)** for workspace-based dependency management.

## Trade-off Matrix

| Feature | uv (Chosen) | pip | Poetry / PDM |
| :--- | :--- | :--- | :--- |
| **Speed** | 10-100x faster (Rust-based) | Baseline | Moderate |
| **Locking** | Unified `uv.lock` for workspace | Manual `requirements.txt` | Per-project lockfiles |
| **Monorepo Support** | Native Workspaces | None (Native) | Plugin-based or complex |
| **Tooling** | Single binary for all | Multiple tools needed | Heavy runtime |

## Justification
`uv` allows us to define a single source of truth for the entire monorepo. The unified locking mechanism prevents "dependency drift" between the `backend` and auxiliary scripts. Its extreme performance significantly reduces Docker build times and CI latency, which is essential for the 15-day MVP timeline.

## Consequences
- **Positive**: Blazing fast environment setup, bit-perfect reproduction via `uv sync --frozen`, and simplified monorepo structure.
- **Negative**: Adds a specific tool dependency to the developer workflow (though easily installable via `brew`, `curl`, or `pip`).
