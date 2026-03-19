---
name: reference-repos
description: >
  Permanent reference library of 7 GitHub repositories that MUST be consulted for every technical question.
  These repos represent working reference implementations of LLM apps, multi-model routing, LLM evaluation
  (DeepEval, promptfoo), CI pipelines, observability, agentic AI course material (NUS-ISS), Docker/Kubernetes
  deployment patterns, multi-agent workflows, and 734+ cybersecurity skills mapped to MITRE ATT&CK, OWASP,
  and NIST CSF. Always read relevant files from these repos before answering coding questions, choosing
  patterns, or recommending approaches for the TraceData project.
---

# Reference Repository Library

## HOW TO USE THIS SKILL

Whenever you receive a question about code, architecture, testing, CI/CD, agents, or deployment:

1. **Identify** which repo(s) below are relevant.
2. **Fetch** the specific file from GitHub raw content: `https://raw.githubusercontent.com/<owner>/<repo>/main/<path>`
3. **Use** the patterns you find as the primary reference — prefer these over generic approaches.

---

## Repository Map

### 1. `darryl1975/llmapp` — LLM App v1 (Baseline)
**URL:** https://github.com/darryl1975/llmapp
**What it is:** The foundational LLM application. Dual implementation: Spring Boot + Spring AI (Java) and FastAPI (Python).
**Key patterns:**
- `llm-python/` — FastAPI service with controller/service/dto layering
  - `app/service/ai_service.py` — Core LLM call patterns (sentiment, classify, intent, summarize)
  - `app/controller/ai_controller.py` — FastAPI route definitions
  - `app/dto/` — Pydantic response models (SentimentResponse, ClassificationResponse, IntentResponse, SummaryResponse)
  - `tests/test_ai_service.py`, `tests/test_ai_controller.py` — pytest unit test patterns
- `llm/` — Spring Boot + Spring AI backend
  - `src/main/java/.../service/AIService.java` — Java LLM service layer
  - `src/main/java/.../controller/AIController.java` — REST controller
  - `src/main/java/.../dto/` — Java DTOs
  - `src/test/java/.../AIServiceTest.java`, `AIControllerTest.java` — JUnit unit tests
- `llm-frontend-python/` — Flask frontend calling the Python API
**Use for:** Basic LLM API structure, DTO patterns, unit test patterns (both Python and Java).

---

### 2. `darryl1975/llmapp04` — LLM App v4 (Multi-Model Routing + Evaluation)
**URL:** https://github.com/darryl1975/llmapp04
**What it is:** Adds multi-model routing and LLM evaluation (DeepEval + promptfoo) to the v1 baseline.
**Key patterns:**
- `llm-multiroute/` — Multi-model routing layer
  - `app/router/model_router.py` — LLM routing logic (route by task type to best model)
  - `app/service/ai_service.py` — Extended service with multi-model support
  - `app/config.py` — Multi-model config (Gemini, GPT-4o, etc.)
- `deepeval-tests/` — LLM evaluation with DeepEval
  - `DEEPEVAL_INSTRUCTIONS.md` — How to set up and run DeepEval
  - `test_sentiment.py`, `test_classify.py`, `test_intent.py`, `test_summarize.py` — Metric-based LLM test patterns
  - `api_client.py` — HTTP client for calling the LLM API in tests
  - `conftest.py` — pytest fixtures for DeepEval
- `promptfoo-tests/` — Prompt regression testing
  - `sentiment.yaml`, `classify.yaml`, `intent.yaml`, `summarize.yaml` — promptfoo config files
  - `PROMPTFOO_INSTRUCTIONS.md` — How to set up promptfoo
- `llm-python/jmeter/` — JMeter load test plan for the summarize endpoint
**Use for:** Multi-model routing, DeepEval test structure, promptfoo config, JMeter load testing.

---

### 3. `darryl1975/llmapp05` — LLM App v5 (Docker + CI/CD)
**URL:** https://github.com/darryl1975/llmapp05
**What it is:** Adds Docker containerisation, GitHub Actions CI, and Kubernetes deployment to v4.
**Key patterns:**
- `.github/workflows/` — GitHub Actions CI pipelines
  - `deepeval-tests-ci.yml` — CI for DeepEval LLM quality gate
  - `promptfoo-tests-ci.yml` — CI for promptfoo prompt regression tests
  - `llm-multiroute-ci.yml` — CI for the Python multi-route service (lint + unit tests)
  - `llm-frontend-python-ci.yml` — CI for the Flask frontend
- `llm-multiroute/Dockerfile` — Production Dockerfile for the Python API
- `llm-multiroute/k8s/deployment.yaml` — Kubernetes deployment manifest
- `llm-frontend-python/k8s/deployment.yaml` — Kubernetes deployment for frontend
- `docker-compose.yml` — Local dev compose (multi-route + frontend)
**Use for:** CI workflow patterns for Python services, Docker best practices, Kubernetes deployment structure.

---

### 4. `darryl1975/llmapp06` — LLM App v6 (Observability + Safety)
**URL:** https://github.com/darryl1975/llmapp06
**What it is:** Adds production observability (metrics collection, cost tracking) and safety checking to v5.
**Key patterns:**
- `llm-multiroute/app/monitoring/` — Observability layer
  - `metrics_store.py` — In-process metrics collection (latency, token count, cost per request)
  - `safety_checker.py` — Input safety validation (content filtering before LLM call)
- `llm-multiroute/metrics/` — Captured metrics JSON files
  - `cost_metrics.json` — Cost per model per endpoint
  - `performance_metrics.json` — Latency/throughput per endpoint
  - `safety_metrics.json` — Safety check results and flagged inputs
- `llm-multiroute/metrics_testing.md` — Documentation on how observability was tested
- `llm-multiroute/app/controller/ai_controller.py` — Extended controller with monitoring hooks
**Use for:** Metrics collection patterns, cost tracking, safety checker, observability integration into FastAPI.

---

### 5. `darryl1975/gradingapp` — Multi-Agent Grading App (Real Multi-Service Pattern)
**URL:** https://github.com/darryl1975/gradingapp
**What it is:** A multi-agent application where a `platform-backend` orchestrates two specialist agents (`grading-agent` and `review-agent`). Shows real microservice-style agent coordination with streaming responses.
**Key patterns:**
- `platform-backend/` — Orchestrator service
  - `services/agent_client.py` — HTTP client for calling downstream agents (how to call an agent from another service)
  - `services/stream_merger.py` — NDJSON streaming merger (combines streams from multiple agents)
  - `routers/process.py` — Endpoint that triggers the multi-agent pipeline
- `grading-agent/` — Specialist grading agent (FastAPI + LLM)
  - `services/grader.py` — Scoring logic using structured LLM output
  - `routers/grade.py` — `/grade` endpoint
- `review-agent/` — Specialist review agent (FastAPI + LLM)
  - `services/reviewer.py` — Review/feedback generation logic
  - `routers/review.py` — `/review` endpoint
- `frontend/` — Vite + React frontend
  - `src/hooks/useEssayStream.js` — Streaming hook for NDJSON response handling
  - `src/utils/ndjsonParser.js` — NDJSON parser utility
  - `src/components/GradingPanel.jsx`, `ReviewPanel.jsx`, `ScoreCard.jsx` — UI components
- `docker-compose.yml` — Full stack compose (3 backends + frontend)
**Use for:** Multi-agent orchestration patterns, streaming LLM responses end-to-end, frontend SSE/NDJSON handling, Docker compose for multi-service AI stacks.

---

### 6. `uzyn/agentic-ai-course` — NUS-ISS Instructor's Course Repo (Canonical Reference)
**URL:** https://github.com/uzyn/agentic-ai-course
**What it is:** The instructor's (uzyn = U-Zyn Chua, NUS-ISS) official course material for "Architecting Agentic AI Solutions". This is the **canonical source of truth** for course patterns.
**Key patterns:**
- `1-module/` — Module 1: Embeddings
  - `embeddings.ipynb` — Embeddings fundamentals notebook
- `1-workshop/` — Workshop 1: LLM Basics
  - `workshop.ipynb` — Workshop notebook with structured extraction, prompt engineering
  - `assignment.md` — Workshop 1 assignment spec
- `3-module/` — Module 3: Multi-Agent Frameworks (THE MOST RELEVANT MODULE)
  - `d1-openai-agents-demo.ipynb` — OpenAI Agents SDK demo
  - `d2l-local-mcp/server.py` — Local MCP server implementation
  - `d2l-mcp-demo-stdio.ipynb` — MCP stdio demo notebook (**Context Enrichment Tool reference**)
  - `d2r-mcp-demo-remote.ipynb` — Remote MCP demo
  - `d3-smolagents-demo.ipynb` — smolagents demo (**Support Agent coaching reference**)
  - `d4-autogen-demo.ipynb` — AutoGen multi-agent demo
  - `d5-crewai-demo.ipynb` — CrewAI demo
  - `d6-langgraph-demo.ipynb` — LangGraph demo (**Safety Agent cyclical flow reference**)
- `3-workshop/` & `3-workshop-starter/` — Workshop 3: Multi-Agent System (Singapore context!)
  - `agents/orchestrator.py` — Orchestrator agent pattern (**Orchestrator Agent reference**)
  - `agents/participant.py` — Participant/specialist agent pattern
  - `agents/summarizer.py` — Summarizer agent
  - `nodes.py` — LangGraph node definitions
  - `state.py` — LangGraph shared state definition
  - `tools/singapore_weather.py` — Singapore weather MCP tool (**Context Tool reference**)
  - `tools/singapore_news.py` — Singapore news tool
  - `tools/singapore_time.py` — Singapore time tool
  - `main.py`, `utils.py` — Entry point and utilities
**Use for:** Canonical patterns for LangGraph state/nodes, orchestrator agent, MCP tools, Singapore-specific tool integration. Always prefer these patterns over generic tutorials.

### 7. `sree-r-one/Anthropic-Cybersecurity-Skills` — 734+ Cybersecurity Skills Library
**URL:** https://github.com/sree-r-one/Anthropic-Cybersecurity-Skills
**What it is:** A curated library of **734+ cybersecurity skills** built to the [agentskills.io](https://agentskills.io) open standard. Each skill covers a specific security technique or threat analysis procedure, with MITRE ATT&CK, OWASP, and NIST CSF mappings. This is the user's own repo.
**Structure:**
- `skills/<skill-name>/SKILL.md` — Step-by-step skill instructions
- `skills/<skill-name>/scripts/agent.py` — Python agent that executes the skill
- `skills/<skill-name>/references/` — API references, standards, workflows for the skill
- `mappings/mitre-attack/coverage-summary.md` — MITRE ATT&CK coverage across all skills
- `mappings/owasp/README.md` — OWASP mapping
- `mappings/nist-csf/csf-alignment.md` — NIST CSF alignment
- `index.json` — Machine-readable index of all 734+ skills
**Relevant skill categories for TraceData:**
- **Log analysis**: `analyzing-api-gateway-access-logs`, `analyzing-security-logs-with-splunk`, `analyzing-linux-audit-logs-for-intrusion`, `analyzing-kubernetes-audit-logs`
- **Network forensics**: `analyzing-network-traffic-for-incidents`, `analyzing-dns-logs-for-exfiltration`, `analyzing-network-flow-data-with-netflow`
- **Container security**: `analyzing-docker-container-forensics`
- **Threat intelligence**: `analyzing-threat-intelligence-feeds`, `analyzing-indicators-of-compromise`, `analyzing-apt-group-with-mitre-navigator`
- **Cloud security**: `analyzing-azure-activity-logs-for-threats`, `analyzing-cloud-storage-access-patterns`
**Use for:** Security incident analysis procedures, threat detection patterns, MITRE ATT&CK lookup, OWASP vulnerability reference, NIST CSF compliance. Fetch any skill with:
`https://raw.githubusercontent.com/sree-r-one/Anthropic-Cybersecurity-Skills/main/skills/<skill-name>/SKILL.md`

---

## Quick Lookup Table

| I need to...                                  | Primary Repo                        | Key File(s)                                                       |
| :-------------------------------------------- | :---------------------------------- | :---------------------------------------------------------------- |
| Build a FastAPI LLM service                   | `llmapp`                            | `llm-python/app/service/ai_service.py`                            |
| Route requests to different models            | `llmapp04`                          | `llm-multiroute/app/router/model_router.py`                       |
| Write DeepEval LLM tests                      | `llmapp04/05`                       | `deepeval-tests/test_sentiment.py` (pattern)                      |
| Set up promptfoo prompt tests                 | `llmapp04/05`                       | `promptfoo-tests/sentiment.yaml`                                  |
| Set up GitHub Actions CI for Python           | `llmapp05`                          | `.github/workflows/llm-multiroute-ci.yml`                         |
| Containerise a FastAPI service                | `llmapp05`                          | `llm-multiroute/Dockerfile`                                       |
| Add observability/metrics to FastAPI          | `llmapp06`                          | `app/monitoring/metrics_store.py`                                 |
| Add safety checking                           | `llmapp06`                          | `app/monitoring/safety_checker.py`                                |
| Build multi-agent orchestration               | `gradingapp`                        | `platform-backend/services/agent_client.py`                       |
| Stream LLM responses to frontend              | `gradingapp`                        | `frontend/src/hooks/useEssayStream.js`                            |
| Implement MCP tool (Singapore)                | `agentic-ai-course`                 | `3-module/d2l-mcp-demo-stdio.ipynb`                               |
| Build LangGraph orchestrator                  | `agentic-ai-course`                 | `3-workshop/agents/orchestrator.py`                               |
| Define LangGraph state                        | `agentic-ai-course`                 | `3-workshop/state.py`                                             |
| Get Singapore-specific tools                  | `agentic-ai-course`                 | `3-workshop/tools/singapore_weather.py`                           |
| Analyse API/log security incidents            | `Anthropic-Cybersecurity-Skills`    | `skills/analyzing-api-gateway-access-logs/SKILL.md`               |
| Detect DNS exfiltration                       | `Anthropic-Cybersecurity-Skills`    | `skills/analyzing-dns-logs-for-exfiltration/SKILL.md`             |
| Analyse network traffic for threats           | `Anthropic-Cybersecurity-Skills`    | `skills/analyzing-network-traffic-for-incidents/SKILL.md`         |
| Look up MITRE ATT&CK technique coverage       | `Anthropic-Cybersecurity-Skills`    | `mappings/mitre-attack/coverage-summary.md`                       |
| Look up OWASP vulnerability mapping           | `Anthropic-Cybersecurity-Skills`    | `mappings/owasp/README.md`                                        |
| Check NIST CSF alignment                      | `Anthropic-Cybersecurity-Skills`    | `mappings/nist-csf/csf-alignment.md`                              |
| Analyse container/Docker security             | `Anthropic-Cybersecurity-Skills`    | `skills/analyzing-docker-container-forensics/SKILL.md`            |
