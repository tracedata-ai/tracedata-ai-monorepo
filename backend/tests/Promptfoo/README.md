# Promptfoo-style adversarial / prompt-safety tests (TraceData)

This folder holds **pytest-based** tests inspired by [Promptfoo](https://www.promptfoo.dev/) red-team
workflows. They validate **current TraceData prompt contracts and local fallback behavior** (no
`npx promptfoo`, no live LLM calls in the default path).

## Contents

| File | Role |
|------|------|
| `test_prompt_safety_contract.py` | Asserts key lines in the sentiment explanation system prompt; checks deterministic explanation fallback when no LLM is configured. |
| `test_promptfoo_50_case_scale.py` | **48** parameterized adversarial / injection / harmful / PII-style strings; each run uses the same deterministic `_build_explanation` fallback. |

Together this suite is **50** pytest items (2 + 48).

## What is exercised

- [`agents/sentiment/agent.py`](../../agents/sentiment/agent.py):
  `SENTIMENT_EXPLANATION_SYSTEM_PROMPT` and `_build_explanation` (with `_llm = None`).

## How to run

From the `backend` directory:

```bash
# Entire Promptfoo folder
uv run pytest tests/Promptfoo -v

# Only the 50-case scale (parameterized)
uv run pytest tests/Promptfoo/test_promptfoo_50_case_scale.py -v
```

## Markers

- All Promptfoo tests: `xai`, `eval`
- Parameterized adversarial scale: also `external` (reserved for future CLI / API-gated runs; today
  the tests stay offline)
- **`nightly`** on the 48-case scale: excluded from **PR** backend API pytest (`-m "not nightly"`); included in the scheduled workflow `.github/workflows/ci-backend-eval-nightly.yaml` on **`main`**.

See `[tool.pytest.ini_options]` in `pyproject.toml`.

## CI

- **PR** (`ci-backend-api`): runs `pytest … -m "not nightly" tests/` — the 48-case file is **skipped** on PR; `test_prompt_safety_contract.py` (2 tests) still runs on PR.
- **`main` nightly**: `ci-backend-eval-nightly` runs **full** `pytest tests/` (includes `nightly`).

## Future extension

When you add real Promptfoo configs (`promptfooconfig.yaml`) and `npx promptfoo eval`, keep those
runs in a separate optional or scheduled job with secrets and cost controls; keep this pytest suite
as the fast, deterministic layer.
