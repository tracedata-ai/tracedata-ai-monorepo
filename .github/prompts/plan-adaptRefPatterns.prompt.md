# Plan: Adapt Reference Agent Patterns to Backend/Agents

## TL;DR

Systematically integrate reference patterns (LangGraph + LLM adapters + tools + domain modules) into your existing backend/agents infrastructure. Start with a minimal proof-of-concept agent to validate the pattern in-place, then progressively enhance all agents. Keep the working orchestration engine; add LLM layer on top via coexistence strategy (v1 stubs + v2 LLM agents, switchable via env var).

---

## Steps

### **PHASE 1: Minimal Proof-of-Concept** *(1-2 days, validates entire pattern)*

1. **Create LLM adapter layer**: [backend/common/llm/]
   - Port `LLMAdapter` ABC + `OpenAIAdapter`, `AnthropicAdapter`, factory `load_llm()` from references
   - No changes needed, reuse as-is

2. **Create tools directory**: [backend/agents/tools/]
   - Add `weather_traffic.py` (@tool functions from reference)

3. **Create minimal agent**: [backend/agents/examples/weather_traffic_agent.py]
   - Copy `ExampleWeatherTrafficAgent` from reference
   - Backport `Agent` ABC to [backend/agents/base/agent_llm.py]

4. **Create system prompts config**: [backend/common/config/system_prompts.py]
   - Enum + dict mapping agent types to prompts (copied from reference)

5. **Test PoC offline**: `pytest tests/agents/test_weather_example.py`
   - LLM + tools, no Redis needed

---

### **PHASE 2: Tool Ecosystem** *(2-3 days, depends on Phase 1)*

1. **Create domain tools**: [backend/agents/tools/]
   - Add `safety_tools.py`, `scoring_tools.py`, `sentiment_tools.py`, `support_tools.py`
   - @tool decorated functions reading from Redis/DB

2. **Create Redis helpers**: [backend/agents/tools/redis_helpers.py]
   - Wrapper with graceful demo data fallbacks

3. **Create orchestrator tools**: [backend/agents/orchestrator/orchestrator_tools.py]
   - `get_event_config()`, `evaluate_coaching_rules()` adapted to existing EVENT_MATRIX

4. **Extend ScoringAgent**: [backend/agents/scoring/agent_v2.py]
   - NEW (inherit from `Agent` ABC + scoring_tools)

5. **Test tools**: `pytest tests/agents/test_tools.py`, `tests/agents/test_scoring_agent_v2.py`

---

### **PHASE 3: LLM Layer Integration** *(1-2 days, depends on Phases 1-2, blocks Phase 4)*

1. **Modify [backend/agents/base/agent.py]**
   - Add optional `llm`, `tools`, `system_prompt` params
   - Add `_invoke_llm()` method for LLM orchestration
   - Backward compatible, stubs still work

2. **Create agent v2 wrappers**: [backend/agents/*/agent_v2.py] *(4 files)*
   - `SafetyAgent`, `ScoringAgent`, `SentimentAgent`, `SupportAgent` v2 with LLM enabled

3. **Update agent startup**: [backend/agents/worker.py]
   - Add env var `ENABLE_LLM_AGENTS=true/false`
   - Add `LLM_PROVIDER=openai|anthropic`
   - Add `LLM_MODEL=gpt-4o|claude-opus`

4. **Celery tasks**: [backend/agents/*/tasks.py]
   - No changes (they call `agent.process_event()` which now optionally uses LLM)

5. **Add observability**: [backend/agents/base/agent_observer.py]
   - Track model, tokens, latency, tool calls

---

### **PHASE 4: Domain Modules (XAI + Fairness)** *(2-3 days, depends on Phase 2)*

1. **Create SHAPExplainer**: [backend/agents/scoring/xai.py]
   - Port from reference (demo: hardcoded values, real XGBoost later)

2. **Create FairnessAuditor**: [backend/agents/scoring/fairness.py]
   - Port from reference (demo: hardcoded metrics, real AIF360 later)

3. **Enhance ScoringAgent v2**
   - Compose Explainer + Auditor
   - After LLM score, call `explain()` + `audit()` to merge SHAP + fairness audit into result dict

4. **Add XAI tools**: [backend/agents/scoring/scoring_tools.py]
   - Extend with `get_raw_features()`, `get_driver_demographics()` for XAI/fairness

5. **Test XAI**: `pytest tests/agents/test_scoring_xai.py`

---

### **PHASE 5: Execution Workflow & Security** *(1-2 days, depends on Phase 3)*

1. **Port ExecutionWorkflow**: [backend/common/config/execution_workflow.py]
   - `ExecutionPolicy`, `AgentSequenceStep`, `ExecutionWorkflow` from reference

2. **Enhance IntentCapsule**: [backend/common/models/intent_capsule.py]
   - Add `execution_workflow`, `scoped_redis_token` (HMAC-signed) fields

3. **Add scope enforcement**: [backend/agents/base/agent.py]
   - Validate agent allowed to read/write scoped keys
   - Log security events

---

### **PHASE 6: Observability & Monitoring** *(1-2 days, depends on Phases 3-4)*

1. **Enhance agent observer**: [backend/agents/base/agent_observer.py]
   - Structured JSON logs (model, tokens, latency, cost, tool latencies)
   - Publish to Datadog/ELK

2. **Add LLM cost tracking**: [backend/common/config/llm_costs.py]
   - Model → cost per 1K tokens
   - Observer calculates cost per invocation

3. **Create observability README**: [backend/agents/OBSERVABILITY.md]
   - Logging guide, cost queries, performance metrics

---

## Relevant Files

### To Create (32 new files across 6 phases)

**LLM Adapters & Configuration:**
- backend/common/llm/adapter.py
- backend/common/llm/factory.py
- backend/common/llm/models.py
- backend/common/config/system_prompts.py
- backend/common/config/execution_workflow.py
- backend/common/config/llm_costs.py

**Agent Base & Observability:**
- backend/agents/base/agent_llm.py
- backend/agents/base/agent_observer.py

**Tools Layer:**
- backend/agents/tools/base.py
- backend/agents/tools/weather_traffic.py
- backend/agents/tools/safety_tools.py
- backend/agents/tools/scoring_tools.py
- backend/agents/tools/sentiment_tools.py
- backend/agents/tools/support_tools.py
- backend/agents/tools/redis_helpers.py
- backend/agents/orchestrator/orchestrator_tools.py

**Example & Domain Agents:**
- backend/agents/examples/weather_traffic_agent.py
- backend/agents/safety/agent_v2.py
- backend/agents/scoring/agent_v2.py
- backend/agents/scoring/xai.py
- backend/agents/scoring/fairness.py
- backend/agents/sentiment/agent_v2.py
- backend/agents/driver_support/agent_v2.py

**Tests (8 files):**
- tests/agents/test_weather_example.py
- tests/agents/test_tools.py
- tests/agents/test_scoring_agent_v2.py
- tests/agents/test_scoring_xai.py
- tests/agents/test_agent_integration.py
- tests/security/test_scope_enforcement.py
- tests/observability/test_logging.py

**Documentation:**
- backend/agents/OBSERVABILITY.md

### To Modify (minimal changes, backward compatible)

- backend/agents/base/agent.py — Phase 3: add llm/tools/prompt params + `_invoke_llm()` method
- backend/agents/worker.py — Phase 3: add LLM env var parsing + agent initialization
- backend/agents/*/tasks.py — Phase 3: verify they call `agent.process_event()` (no code changes, just validation)
- backend/common/models/intent_capsule.py — Phase 5: add workflow + scoped_token fields

### Already Exist (reuse as-is, no changes)

- backend/common/config/events.py — EVENT_MATRIX (source of truth for routing)
- backend/common/redis/ — Redis client library
- backend/agents/orchestrator/agent.py — Orchestration engine (intact)
- backend/agents/orchestrator/db_manager.py — DB locking (intact)
- Celery configuration — use as-is

---

## Verification

### Phase 1 Verification
```
1. Run test: pytest tests/agents/test_weather_example.py
   → Verify: PoC agent loaded, LLM called, result dict returned
   
2. Manual test: 
   from backend.common.llm import load_llm, OpenAIModel
   llm = load_llm(OpenAIModel.GPT_4O).adapter.get_chat_model()
   → Verify: Chat model initialized, API key loaded from env
   
3. Tool test:
   from backend.agents.tools import weather, traffic
   result = weather("Singapore")
   → Verify: Tool returns formatted string, no errors
```

### Phase 2 Verification
```
1. Run test: pytest tests/agents/test_scoring_agent_v2.py
   → Verify: Scoring agent loads, calls tools, LLM reasons about data
   
2. Tool test:
   from backend.agents.scoring.scoring_tools import get_trip_context
   ctx = get_trip_context("TRIP-T123")
   → Verify: Dict returned with expected keys, can pass to LLM
   
3. Integration test:
   agent.invoke_with_trip("TRIP-T123")
   result = json.loads(...)
   → Verify: Score, label, coaching_required all present
```

### Phase 3 Verification
```
1. Run test: pytest tests/agents/test_agent_integration.py
   → Verify: TDAgentBase accepts llm param, calls LLM on process_event
   
2. Environment override test:
   ENABLE_LLM_AGENTS=false python -m agents.worker scoring
   → Verify: Agent uses stub (existing behavior)
   
   ENABLE_LLM_AGENTS=true LLM_PROVIDER=openai LLM_MODEL=gpt-4o python -m agents.worker scoring
   → Verify: Agent loads LLM, uses it in process_event
```

### Phase 4 Verification
```
1. Run test: pytest tests/agents/test_scoring_xai.py
   → Verify: Score + SHAP explanation + fairness audit returned
   
2. Manual test:
   result = scoring_agent.invoke_with_trip("TRIP-T123")
   → Parse result, verify shap_explanation.top_features present
   → Verify fairness_audit.bias_detected is bool, recommendation is str
```

### Phase 5 Verification
```
1. Run test: pytest tests/security/test_scope_enforcement.py
   → Verify: Agent respects capsule scope, rejects unauthorized access
```

### Phase 6 Verification
```
1. Run agent with logging enabled:
   python -m agents.worker scoring 2>&1 | grep -i "tokens\|cost\|latency"
   → Verify: Structured logs contain model, tokens, cost, latency
```

---

## Decisions

- **Coexistence strategy**: Keep stub agents (v1) + add LLM agents (v2) in parallel. Switch via env var for safe rollout.
- **Demo-first approach**: Phase 4 uses hardcoded SHAP/fairness data. Real ML models (XGBoost, AIF360) in future sprint.
- **No breaking changes**: Orchestrator + DBManager + Celery stay intact. LLM layer is additive.
- **Vendor-free**: Reference patterns are being vendored into backend (copied code), not imported as external package.
- **Progressive infrastructure**: Start with hardcoded Redis lookups, evolve to caching/pooling later.
- **LLM provider flexibility**: Adapter pattern allows easy OpenAI ↔ Anthropic switching.

---

## Further Considerations

### 1. LLM Token Budgets
Should we implement hard limits on tokens per agent? (e.g., ScoringAgent max 4K input tokens)

**Recommendation**: Add in Phase 6 observability; for now, log and monitor.

### 2. Fallback Strategy
If LLM fails, should agents degrade to stubs or fail the task?

**Recommendation**: Phase 3 — add graceful degradation: LLM timeout → log warning → return best-effort stub result (scoring=85, support="generic tip").

### 3. Async Tool Calls
Some tools might need async Redis reads. Should tools be async?

**Recommendation**: Phase 2 — define all scoring tools as async; LangChain handles async/sync conversion automatically via @tool.

### 4. Peer Group Averaging
Reference mentions it deferred. Should we implement now?

**Recommendation**: Phase 2+ — infrastructure exists in EVENT_MATRIX. Implement benchmarking queries in separate sprint (depends on data volume).

---

## Summary

This plan provides a structured path to integrate advanced agent patterns while:
- ✅ Keeping existing infrastructure (Orchestrator, DBManager, Celery) intact
- ✅ Enabling graceful fallback (v1 stubs → v2 LLM-driven)
- ✅ Starting with a minimal PoC to validate approach
- ✅ Building toward full XAI + fairness capabilities
- ✅ Maintaining flexibility across LLM providers

**Next**: Approve this plan or request refinements, then begin Phase 1 implementation.
