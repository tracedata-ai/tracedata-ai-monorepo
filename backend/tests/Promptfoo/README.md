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

See `[tool.pytest.ini_options]` in `pyproject.toml`.

## CI

**Not integrated into CI yet.** Run locally until a pipeline step is added (e.g. PR vs nightly split
for any future real Promptfoo CLI or live-model evals).

## Future extension

When you add real Promptfoo configs (`promptfooconfig.yaml`) and `npx promptfoo eval`, keep those
runs in a separate optional or scheduled job with secrets and cost controls; keep this pytest suite
as the fast, deterministic layer.
