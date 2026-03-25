# Troubleshooting Guide

This document tracks recurring engineering issues using a standard KB format.

Identifier pattern:
KB-<DOMAIN>-<AREA>-<SEQUENCE>

Examples:

- KB-BE-CI-001 (Backend CI)
- KB-FE-BUILD-002 (Frontend build)

## KB-BE-CI-001 | Backend CI formatting check fails (Ruff)

### Metadata

| Field      | Value                                 |
| ---------- | ------------------------------------- |
| Topic      | CI/CD Pipeline                        |
| Domain     | Backend                               |
| Area       | Code Quality / Formatting             |
| Issue Type | Tooling Policy Mismatch               |
| Severity   | S3 (Build blocked, no runtime outage) |
| Status     | Active                                |
| Tags       | backend, ci, ruff, formatting, lint   |
| Owner      | Backend Team                          |

### Issue statement

Backend CI fails in lint stage because at least one file is not formatted according to Ruff rules.

### Typical symptom

The pipeline reports that a file would be reformatted, for example:

- backend/app/core/middleware.py

### Detection point

Formatting is enforced in backend CI using:

- uv run ruff format --check .

Configured in:

- .github/workflows/ci-backend-api.yaml
- backend/pyproject.toml

### Root cause

Local changes were committed without running the same formatter check that CI enforces.

### Resolution (targeted file fix)

Run from repository root:

    cd backend
    uv sync --frozen --extra dev
    uv run ruff format app/core/middleware.py
    uv run ruff format --check .
    uv run ruff check .

Commit and push:

    git add app/core/middleware.py
    git commit -m "style: format middleware with ruff"
    git push

### Resolution (all backend files)

Use this when multiple files may be affected:

    cd backend
    uv sync --frozen --extra dev
    uv run ruff format .
    uv run ruff check .

### Prevention

- Run formatter locally before every push.
- Keep editor format-on-save aligned to Ruff.
- Prefer Ruff as source of truth for backend formatting checks.

### Notes

- Black-only formatting can still fail this pipeline if it differs from Ruff output.
