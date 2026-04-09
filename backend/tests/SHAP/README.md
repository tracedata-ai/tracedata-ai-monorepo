# SHAP-style explainability tests (TraceData)

This folder holds **feature-importance / explanation contract tests** for trip scoring. They assert
the shape and stability of **`shap_explanation`** on the deterministic scoring path. They do **not**
call the [SHAP](https://github.com/slundberg/shap) Python package (the payload uses a heuristic method
label today).

## What is exercised

- [`agents/scoring/features.py`](../../agents/scoring/features.py): `deterministic_payload_from_bundle`,
  `merge_graph_json_with_baseline`, and the nested `shap_explanation` structure.

## How to run

From the `backend` directory:

```bash
uv run pytest tests/SHAP -v
```

## Markers

Tests use `xai` and `eval` (see `pyproject.toml`).

## CI

These tests are wired into CI:

- **Nightly** (`ci-backend-eval-nightly`): runs the full `tests/SHAP` suite and publishes JUnit artifacts.
- **PR/API CI smoke** (`ci-backend-api`): runs a targeted explainability contract test via
  `tests/SHAP/test_scoring_explainability_contract.py`.
