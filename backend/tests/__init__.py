"""
TraceData Backend — Test Suite.

Tests are organised by layer:
  tests/unit/       → Pure logic (schemas, utils) — no DB
  tests/integration → API endpoints with a real test DB (spun up in CI via service container)

Run locally (requires a running DB):
    DATABASE_URL=postgresql+asyncpg://... uv run pytest -v tests/

Run in CI:
    The ci-backend-api.yaml job injects DATABASE_URL automatically.
"""
