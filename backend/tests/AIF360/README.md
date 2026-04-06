# AIF360-style fairness tests (TraceData)

This folder holds **fairness-adjacent contract tests** for TraceData. They do not require the IBM
[AIF360](https://github.com/Trusted-AI/AIF360) library for the main assertions. One optional test
checks whether `aif360` is installed and skips if not.

## What is exercised

- [`agents/scoring/features.py`](../../agents/scoring/features.py): `fairness_audit` on the
  deterministic scoring payload, and merge behavior when LLM JSON omits fairness fields.

## How to run

From the `backend` directory:

```bash
uv run pytest tests/AIF360 -v
```

Optional: install AIF360 in your environment if you want the optional import test to run instead of skip.

## Markers

Tests use `xai` and `eval`. The optional dependency probe uses `external` (see `pyproject.toml`).

## CI

These tests are **not wired into CI yet**; run them locally or in your own workflow until integration
is added.
