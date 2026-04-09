# LIME-style explainability tests (TraceData)

This folder holds **text explainability–style tests** aligned with how TraceData scores sentiment
today: **keyword anchors** and bounded emotion scores, not the full [LIME](https://github.com/marcotcr/lime)
library.

## What is exercised

- [`agents/sentiment/agent.py`](../../agents/sentiment/agent.py): `EMOTION_ANCHORS`,
  `_score_emotions`, and `_derive_sentiment` thresholds.

## How to run

From the `backend` directory:

```bash
uv run pytest tests/LIME -v
```

## Markers

Tests use `xai` and `eval` (see `pyproject.toml`).

## CI

These tests are wired into CI:

- **Nightly** (`ci-backend-eval-nightly`): runs the full `tests/LIME` suite and publishes JUnit artifacts.
- **PR/API CI smoke** (`ci-backend-api`): runs a targeted explainability contract test via
  `tests/LIME/test_text_anchor_explainability.py`.
