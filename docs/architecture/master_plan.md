# 🚛 TraceData — Master Plan

## AI Intelligence Middleware for Truck Fleet Management

### Multi-Agent System via LangGraph + FastAPI + Kafka

**Team Size:** 4 members **Estimated Effort:** 15 days × 4 = 60 person-days **Target Grade:** A+ **Last Updated:** March 2026 — aligned to all confirmed architectural decisions

---

## 1. The Vision — Brain for Hire

TraceData is not a fleet management system. It is an **AI intelligence middleware** that attaches to existing truck fleet management infrastructure and adds the five capabilities no traditional Fleet Management System (FMS) or Transport Management System (TMS) provides: fairness-audited driver scoring, predictive maintenance, intelligent compliance reasoning, customer sentiment intelligence, and conversational fleet access.

Fleet operators already have systems. They've spent years and significant capital on GPS tracking, trip logging, driver hours recording, and basic reporting. TraceData plugs in on top via a Kafka integration layer — the standard enterprise middleware pattern — without requiring operators to replace anything. In production, one Kafka configuration change connects TraceData to any TMS that can publish telemetry events.

**Why this domain beats brand analytics (EchoChamber):**

- **Safety-critical decisions** — driver fatigue, vehicle failure, compliance violations → explainability is operationally required, not academically contrived
- **Real protected attributes** — driver age in safety scoring affects employment decisions → genuine demographic fairness problem, not a statistical consistency check across brand categories
- **Rich adversarial surface** — GPS spoofing, telemetry tampering, prompt injection in fleet chatbot → deep Module 2 coverage that emerges naturally from the domain
- **Cross-agent intelligence** — correlating vehicle health with driver behaviour with compliance status is something no single model or TMS can do → justifies multi-agent architecture organically
- **Regulatory weight** — Singapore LTA regulations, PDPA for driver data, workplace safety requirements → IMDA MAIGF governance applies meaningfully

**The one sentence that opens every presentation and the group report:**

> _"TraceData is an AI intelligence middleware that attaches to existing fleet management infrastructure via a Kafka integration layer, adding predictive, explainable, and fair decision-making capabilities without requiring operators to replace their current systems."_

---

## 2. Agent Architecture — 4 Agents, 4 Owners

Each team member owns one agent and writes their individual report on that agent. The Orchestrator is Sree's primary individual deliverable and also the system's central coordinator, giving him the richest design story.

### Agent Map & Ownership

| #   | Agent                                    | Owner | Individual Report   | Primary Module                       |
| --- | ---------------------------------------- | ----- | ------------------- | ------------------------------------ |
| 1   | **Orchestrator + Driver Behavior Agent** | Sree  | ✅ Sree writes this | Module 3: Agentic AI                 |
| 2   | **Predictive Maintenance Agent**         | P2    | ✅ P2 writes this   | Module 1: XRAI                       |
| 3   | **Compliance & Safety Agent**            | P3    | ✅ P3 writes this   | Module 2: AI & Cybersecurity         |
| 4   | **Customer Intelligence Agent**          | P4    | ✅ P4 writes this   | Module 4: Integrating & Deploying AI |

### Shared Infrastructure (owned by team, documented in group report)

| Component                       | Owner | Purpose                                                       |
| ------------------------------- | ----- | ------------------------------------------------------------- |
| Kafka consumer + PII middleware | Sree  | Telemetry ingestion, PII masking at middleware layer          |
| LLMRouter                       | Sree  | Centralised OpenAI API caller, model selection, cost tracking |
| AuditLogger                     | P4    | Shared logging class, writes to PostgreSQL audit_log          |
| LangSmith tracing               | P4    | Distributed tracing across all LangGraph nodes                |
| GitHub Actions CI/CD            | P4    | Automated test gates, DigitalOcean deployment                 |
| FaaS truck simulator            | Sree  | Synthetic telemetry with injected age bias                    |

### Why 4 Agents (Not 8)

The original plan had 8 agents. We reduced to 4 for three reasons. First, the briefing specifies 4–5 person teams — 4 agents maps one-to-one with team members, giving each person genuine ownership and a richer individual deliverable. Second, the Route Optimizer and Telemetry Ingestion agents from the original plan are more naturally implemented as infrastructure components (FastAPI Kafka consumer, LLMRouter) than as LangGraph agents — implementing them as agents would add complexity without demonstrating additional agentic capability. Third, the Sentinel monitoring agent is absorbed into P4's shared observability infrastructure — LangSmith + AuditLogger does everything Sentinel would have done without the overhead of a separate agent node.

The result is four agents that are each genuinely rich, each with their own ML model, XAI approach, and security surface — rather than eight agents where some are thin wrappers.

---

## 3. Agent Deep-Dive Designs

### Agent 1: Orchestrator + Driver Behavior Agent (Sree)

**Purpose:** Dual-role agent. As Orchestrator: central coordinator routing all fleet manager requests via LangGraph StateGraph, managing shared FleetState, synthesising cross-agent intelligence, and providing conversational fleet access via an embedded 5-stage RAG pipeline. As Driver Behavior Agent: trains XGBoost on trip telemetry, detects age-based demographic bias with AIF360, corrects with Reweighing, and renders SHAP explanations in the dashboard.

**Why LLM for orchestration (justified):** Fleet manager queries are semantically ambiguous. "What happened with Driver 42?" could be a behaviour query, a maintenance query, or a compliance query. Deterministic decision trees cannot resolve this reliably. GPT-4o-mini classifies intent. GPT-4o handles complex multi-agent synthesis. Cost is controlled through the centralised LLMRouter.

**Two operating modes:**

- Analytical Mode — intent classification → route to agent → synthesise cross-agent response
- Conversational Mode — 5-stage RAG pipeline grounded in live fleet data

**Tools:** `xgboost_scorer`, `aif360_detector`, `aif360_corrector`, `shap_explainer`, `lime_explainer`, `pgvector_retriever`, `query_rewriter`, `db_query_tool`, `alert_dispatcher`

**The XRAI centrepiece:** Disparate Impact Ratio before correction: **0.62** (young drivers scored 38% more harshly than older drivers for equivalent behaviour). After Reweighing: **0.92** (within FEAT fairness threshold of 0.8–1.2). SHAP global feature importance rendered in dashboard. LIME local explanations per driver alert. This is a genuine protected-group fairness problem — not a statistical consistency check across brand categories.

---

### Agent 2: Predictive Maintenance Agent (P2)

**Purpose:** Proactive vehicle health intelligence. Predicts component failures before they cause unplanned downtime. Operates in two LangGraph modes: Reactive (anomaly-triggered) and Proactive (scheduled weekly fleet scan).

**Why agentic (not just an ML endpoint):** Two operating modes controlled by LangGraph conditional edges, autonomous severity decisions (monitor vs schedule vs urgent), memory of vehicle health history, cross-query capability to Driver Behavior Agent for driver-vehicle correlation. This is agent behaviour, not pipeline execution.

**Key design decision — no LLM for prediction:** XGBoost only for failure prediction — justified for auditability, cost efficiency, and SHAP/LIME compatibility. LLM is used only for generating plain-English summaries of LIME output for non-technical fleet managers.

**Tools:** `telemetry_aggregator`, `xgboost_predictor`, `lime_explainer`, `shap_explainer`, `aif360_fleet_auditor`, `anomaly_detector`, `maintenance_scheduler`, `db_query_tool`

---

### Agent 3: Compliance & Safety Agent (P3)

**Purpose:** Intelligent compliance monitoring combining a deterministic rules engine for clear violations with GPT-4o-mini LLM reasoning for edge cases — explicitly distinguishing agentic AI from rules-based automation.

**The hybrid architecture (justified):** Simple checks (hours exceeded, licence expired) use deterministic rules — zero LLM cost, fully auditable. Edge cases ("driver was stationary 2 hours of a 14-hour shift — is this a violation?") require contextual reasoning. LLM is invoked only for ambiguous cases. This directly answers the rubric's hardest question: what does agentic AI provide beyond RPA?

**Security centrepiece (Module 2):** Full STRIDE threat model documented. OWASP LLM Top 10 mitigations. 60+ Promptfoo adversarial tests targeting the LLM reasoning endpoint — inputs attempting to manipulate the LLM into clearing genuine violations.

**Tools:** `rules_engine`, `xgboost_risk_scorer`, `shap_explainer`, `llm_edge_case_reasoner`, `audit_logger`, `compliance_report_generator`, `alert_dispatcher`

---

### Agent 4: Customer Intelligence Agent (P4)

**Purpose:** Proactive RAG-based sentiment intelligence. Goes beyond reactive chatbot — continuously monitors rolling 7-day sentiment scores and autonomously alerts the Orchestrator when complaint thresholds are crossed, without being queried.

**Why proactive beats reactive:** Fleet managers don't have time to query the system — intelligence must come to them. The rolling sentiment monitor acts without being asked. This is genuine agentic behaviour beyond EchoChamber's passive RAG chatbot.

**LLMSecOps centrepiece (Module 4):** LangSmith traces every RAG chain. GitHub Actions CI/CD with mandatory test gates. DigitalOcean App Platform deployment. Cost optimisation: GPT-4o-mini for response drafting, text-embedding-3-small for embeddings.

**Tools:** `sentiment_classifier` (HuggingFace DistilBERT), `xgboost_complaint_categoriser`, `lime_explainer`, `aif360_language_auditor`, `pgvector_store`, `rag_retriever`, `sentiment_monitor`, `response_drafter`, `langsmith_tracer`

---

## 4. The Cross-Agent Demo — The A+ Moment

This scenario is the system's single most important demonstration. It proves TraceData is a genuine multi-agent system, not a pipeline:

1. Maintenance Agent detects Vehicle 07 at high failure risk (brake wear + engine temp spike)
2. Orchestrator cross-queries Driver Behavior Agent — who drove Vehicle 07 this week?
3. Driver Behavior Agent returns — Driver 23, fatigue-flagged from last night's shift
4. Orchestrator cross-queries Compliance Agent — is Driver 23 within legal hours?
5. Compliance Agent returns — Driver 23 is 2 hours over the weekly legal limit
6. Orchestrator synthesises a single unified alert: SHAP reasoning from each agent, plain English summary, two action buttons: **Approve / Escalate**
7. Fleet manager's `human_decision` field (approve/dismiss/escalate) written to AuditLog

No single agent produces this. No traditional TMS produces this. No deterministic pipeline produces this. This is the moment that justifies the architecture.

---

## 5. Module Coverage Matrix

### Module 1: Explainable & Responsible AI (XRAI)

| Requirement             | How TraceData Covers It                                                                          | Agent/Location                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------------- |
| LIME explanations       | Driver risk score feature attribution + vehicle alert explanations                               | Driver Behavior + Maintenance — rendered in dashboard |
| SHAP explanations       | XGBoost feature importance — driver scoring + maintenance prediction + compliance prioritisation | All three ML agents — in dashboard                    |
| AIF360 fairness testing | Driver age bias in safety scoring — DIR 0.62 → 0.92 with before/after metrics                    | Driver Behavior Agent                                 |
| Bias correction         | Reweighing pre-processing, re-tested with AIF360                                                 | Driver Behavior Agent                                 |
| User-facing XAI         | SHAP charts, LIME waterfall, fairness dashboard all visible in Next.js UI                        | Dashboard                                             |
| IMDA MAIGF alignment    | Deep mapping all 4 dimensions with evidence per decision type                                    | Section 5 of report                                   |
| FEAT principles         | Applied to driver scoring — Fairness, Ethics, Accountability, Transparency                       | Driver Behavior Agent design                          |
| Human-in-the-loop       | All consequential decisions require fleet manager approval                                       | All agents via alerts_pending table                   |
| XAI Question Bank       | "Why was this driver flagged?" "Why is this vehicle at risk?" answered directly in UI            | Driver Behavior + Maintenance                         |

### Module 2: AI & Cybersecurity

| Requirement              | How TraceData Covers It                                                                          | Location                                |
| ------------------------ | ------------------------------------------------------------------------------------------------ | --------------------------------------- |
| STRIDE threat model      | Full documented analysis per agent — Spoofing, Tampering, Repudiation, Info Disclosure, DoS, EoP | Section 6 + Compliance Agent design     |
| OWASP LLM Top 10         | Prompt injection, hallucination guard, insecure output handling mapped with mitigations          | All LLM-facing agents                   |
| Prompt injection defense | 3-layer defense: regex guardrails → LLM prompt boundaries → output validation                    | Orchestrator RAG + Compliance LLM       |
| Adversarial testing      | Promptfoo 35+ plugins, 350+ tests, documented pass rate                                          | Testing section                         |
| PII protection           | FastAPI middleware layer — masks before any LLM call                                             | Shared infrastructure                   |
| Data poisoning defense   | Telemetry range validation before ML inference                                                   | Kafka consumer + agent input validation |

### Module 3: Architecting Agentic AI Solutions

| Requirement                         | How TraceData Covers It                                                                                  | Location                              |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------- | ------------------------------------- |
| Multi-agent architecture            | 4 specialised agents + Orchestrator with LangGraph StateGraph                                            | Agent Design section                  |
| Differentiating agentic AI from RPA | Compliance Agent explicitly designed around this distinction — hybrid rules + LLM                        | Compliance Agent design justification |
| Agent autonomy                      | Each agent has reasoning, tools, memory, and planning loop                                               | All agents                            |
| Inter-agent communication           | Shared FleetState via LangGraph, cross-agent queries via Orchestrator                                    | Architecture section                  |
| Framework justification             | LangGraph over CrewAI/AutoGen — justified for StateGraph control and observability                       | Architecture justification            |
| Logical architecture                | 6-layer diagram: Presentation → API Gateway → Orchestration → Business Logic → Data Access → Persistence | Section 3                             |
| Cross-agent coordination            | Primary demo scenario showing 3-agent correlation                                                        | Section 2 + presentation demo         |

### Module 4: Integrating & Deploying AI Solutions

| Requirement           | How TraceData Covers It                                                     | Location                |
| --------------------- | --------------------------------------------------------------------------- | ----------------------- |
| Kafka event streaming | FaaS simulator → Kafka → FastAPI consumer → PostgreSQL                      | Architecture section    |
| CI/CD pipeline        | GitHub Actions: test gate → build → push → deploy to DigitalOcean           | MLSecOps section        |
| LLMSecOps             | LangSmith tracing, prompt hash versioning, cost tracking per agent          | Sentinel infrastructure |
| Containerisation      | Docker modular monolith, three process types from one image                 | Deployment strategy     |
| Automated testing     | Unit + integration + security + XAI + adversarial                           | Testing section         |
| Monitoring            | LangSmith distributed tracing + PostgreSQL AuditLog                         | Shared infrastructure   |
| Async architecture    | Celery + Redis job queue, FastAPI never blocks on LLM                       | Architecture section    |
| Cost optimisation     | LLMRouter with model selection per task type, documented cost per operation | Section 7               |

---

## 6. Tech Stack — Final Confirmed Decisions

| Layer            | Technology                                                  | Justification                                                     |
| ---------------- | ----------------------------------------------------------- | ----------------------------------------------------------------- |
| Agent Framework  | LangGraph + LangChain                                       | StateGraph for complex workflow orchestration                     |
| LLM              | GPT-4o-mini (classification/reasoning) + GPT-4o (synthesis) | Cost-optimised model routing via LLMRouter                        |
| Embeddings       | text-embedding-3-small                                      | 90% cheaper than ada-002, sufficient quality for fleet data       |
| ML Models        | XGBoost                                                     | Interpretable, fast, SHAP/LIME compatible                         |
| Backend          | FastAPI (Python)                                            | Async support, Kafka consumer thread, Celery integration          |
| Frontend         | Next.js 14 + React + Tailwind                               | Dashboard, SHAP charts, RAG chat interface                        |
| Database         | PostgreSQL 17 + pgvector                                    | Unified relational + vector search, audit log, compliance records |
| Task Queue       | Celery + Redis                                              | Async agent execution, decoupled from web server                  |
| Event Streaming  | Kafka                                                       | TMS integration contract, telemetry ingestion                     |
| Observability    | LangSmith + PostgreSQL AuditLog                             | LLM tracing + structured decision logging                         |
| CI/CD            | GitHub Actions                                              | Automated test gates, SHA-based container versioning              |
| Deployment       | DigitalOcean App Platform                                   | Simpler than AWS ECS, production-credible for this scope          |
| Security Testing | Promptfoo                                                   | Adversarial red-team testing, 35+ plugins                         |
| XAI              | SHAP + LIME + AIF360                                        | Course-aligned, well-documented, user-facing                      |

**Explicitly dropped and why:**

| Dropped               | Reason                                                            |
| --------------------- | ----------------------------------------------------------------- |
| RabbitMQ              | Overlaps with Redis/Celery — no clear differentiation             |
| MLflow                | Adds operational complexity, out of scope for 15-day budget       |
| Prometheus + Grafana  | LangSmith + AuditLog covers observability requirements            |
| AWS ECS Fargate       | DigitalOcean App Platform is simpler, equally credible            |
| Local Llama           | Adds 2–3 days of setup complexity, quality worse than GPT-4o-mini |
| Route Optimizer Agent | More infrastructure than agent — better as future enhancement     |
| Sentinel Agent        | Absorbed into shared AuditLogger + LangSmith infrastructure       |

---

## 7. Work Breakdown & 6-Week Timeline

**Total effort: 15 days × 4 members = 60 person-days**

### Phase 1 — Foundation (Week 1)

_Sree leads. Others onboard and prepare._

| Task                                                           | Owner | Days |
| -------------------------------------------------------------- | ----- | ---- |
| Monorepo scaffold, Docker Compose (Kafka + PostgreSQL + Redis) | Sree  | 1    |
| FaaS truck simulator with age bias injection                   | Sree  | 1    |
| FastAPI Kafka consumer + PII middleware                        | Sree  | 1    |
| Celery task queue + bare LangGraph skeleton                    | Sree  | 1    |
| Next.js dashboard showing live telemetry                       | Sree  | 1    |
| XGBoost study + synthetic maintenance data prep                | P2    | 1    |
| Compliance rules engine design + Promptfoo setup               | P3    | 1    |
| GitHub Actions skeleton + DigitalOcean account                 | P4    | 1    |
| Synthetic complaint data generation                            | P4    | 1    |

**Phase 1 exit criteria:** Truck pings flowing through Kafka → PostgreSQL → dashboard. Everyone can run `docker-compose up` and see live data.

### Phase 2 — Agent Intelligence (Weeks 2–3)

_All parallel. One agent per person._

| Task                                                                      | Owner | Days |
| ------------------------------------------------------------------------- | ----- | ---- |
| XGBoost training on trip data, AIF360 bias detection, DIR 0.62 confirmed  | Sree  | 3    |
| Reweighing correction, DIR 0.92 confirmed, SHAP rendering in dashboard    | Sree  | 2    |
| XGBoost failure predictor, LIME per vehicle alert, AIF360 fleet-age check | P2    | 4    |
| Maintenance proactive scheduler, anomaly detector                         | P2    | 2    |
| Rules engine all checks passing, GPT-4o-mini LLM edge case reasoner       | P3    | 3    |
| XGBoost risk scorer + SHAP on violations                                  | P3    | 2    |
| DistilBERT sentiment + XGBoost complaint categoriser + LIME               | P4    | 3    |
| 5-stage RAG pipeline with pgvector, rolling sentiment monitor             | P4    | 2    |

### Phase 3 — Integration + Cross-Agent (Week 4)

_Wire everything through the Orchestrator._

| Task                                                                     | Owner | Days   |
| ------------------------------------------------------------------------ | ----- | ------ |
| LangGraph Orchestrator routing to all 4 agents via intent classification | Sree  | 2      |
| RAG chatbot node added to Orchestrator                                   | Sree  | 1      |
| **Cross-agent demo scenario end-to-end**                                 | All   | 1 each |
| LangSmith tracing confirmed across all agents                            | P4    | 1      |

### Phase 4 — Security + Observability (Week 5)

_Test coverage. Audit trail. Red team._

| Task                                                                  | Owner | Days   |
| --------------------------------------------------------------------- | ----- | ------ |
| Promptfoo config — 35 plugins targeting Orchestrator + Compliance LLM | P3    | 2      |
| Unit + integration tests per agent (target 350+ total)                | All   | 1 each |
| PII middleware tests, AuditLog verified, prompt_hash in all LLM calls | Sree  | 1      |
| GitHub Actions CI/CD with mandatory test gates                        | P4    | 1      |
| DigitalOcean deployment, health checks, rolling deployment            | P4    | 1      |
| STRIDE threat models documented per agent                             | P3    | 1      |

### Phase 5 — Report + Polish (Week 6)

_Write, rehearse, submit._

| Task                                                                                      | Owner | Days     |
| ----------------------------------------------------------------------------------------- | ----- | -------- |
| Group report Sections 1–4 (Executive Summary, System Overview, Architecture, Agent Roles) | All   | 1 each   |
| Group report Sections 5–7 (XRAI, Security, MLSecOps)                                      | All   | 1 each   |
| Individual reports — each member writes 7-section template for their agent                | All   | 2 each   |
| Testing summary — verify test counts, document pass rates                                 | All   | 0.5 each |
| Presentation deck + demo rehearsal (minimum 2 run-throughs)                               | All   | 1 each   |
| Reflection sections, final proof-read, submission                                         | All   | 0.5 each |

---

## 8. Deliverables Checklist

### Group Report Structure

1. **Executive Summary** — project objective, brain-for-hire framing, key highlights, constraints and trade-offs
2. **System Overview** — architecture description, event-driven + interactive query workflows, high-level workflow diagram
3. **System Architecture** — 6-layer logical architecture, DigitalOcean physical deployment, deployment strategy, data flow diagrams, justified architectural choices
4. **Agent Roles and Design** — for each of 4 agents: purpose, reasoning patterns, planning loop, memory, tools, communication, prompt engineering, fallback strategies
5. **Explainable & Responsible AI Practices** — lifecycle alignment, IMDA MAIGF deep mapping, FEAT principles, AIF360 before/after results, SHAP/LIME in UI with screenshots, ethical boundaries as technical constraints
6. **AI Security Risk Register** — STRIDE per agent, OWASP LLM Top 10 mapping, comprehensive risk table, Promptfoo results
7. **MLSecOps / LLMSecOps Pipeline** — CI/CD architecture, test framework, container versioning, deployment strategy, LangSmith + AuditLog monitoring
8. **Testing Summary** — test count table by category and agent, pass rates
9. **Reflection** — team learnings, what we'd do differently

### Individual Report Structure (per member)

1. Introduction — agent purpose in context of the system
2. Agent Design — reasoning pattern, planning loop, memory, tools, communication, prompt engineering, fallback strategies
3. Implementation Details — code structure, tech stack, LLM model choice and justification
4. Testing and Validation — unit, integration, security tests with results
5. Explainable and Responsible AI — which XAI method, which stage, bias check, governance alignment with named frameworks
6. Security Practices — agent-specific STRIDE, mitigations at code level, OWASP LLM mapping
7. Reflection — personal learning journey, honest about challenges, explicit connections to named course concepts ("In XRAI Day 2, we learned about LIME. I applied this when...")

## 9. Risk Mitigation

| Risk                                          | Impact | Mitigation                                                                                                     |
| --------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------- |
| Scope creep                                   | HIGH   | Each agent has a defined MVP. Fancy features are documented as future improvements, not built                  |
| LLM API costs exceed budget                   | MEDIUM | LLMRouter enforces model selection, per-session cost caps, GPT-4o-mini for most calls                          |
| Kafka setup complexity on local machines      | MEDIUM | Docker Compose handles it — `docker-compose up` is the only command needed. Tested on Day 1                    |
| AIF360 installation issues (C++ dependencies) | MEDIUM | Test install before Day 1. Google Colab as fallback for AIF360 experimentation                                 |
| ML model performs poorly on synthetic data    | LOW    | Focus is on XAI demonstration, not model accuracy. SHAP/LIME work regardless of accuracy                       |
| Team member falls behind                      | HIGH   | Agents are loosely coupled — each agent is a standalone Python module. One person's delay doesn't block others |
| DigitalOcean deployment issues                | MEDIUM | Docker Compose local fallback for demo day. Deploy to DigitalOcean in Week 5, not Week 6                       |
| Test count falls short                        | MEDIUM | Promptfoo generates 350+ tests automatically from one config file. Write it in Week 5                          |
| Presentation runs over 20 minutes             | LOW    | Rehearse twice minimum. Cross-agent demo is the centrepiece — everything else supports it                      |

---

## 11. Simulated Data Strategy

**Fleet:** 50 vehicles (V001–V050), varied ages (2015–2023 manufacture year) **Drivers:** 200 drivers (D001–D200), diverse age distribution:

- Young (age 22–30): 40% of drivers — bias injected here
- Mid (age 31–44): 35% of drivers
- Senior (age 45–60): 25% of drivers

**Bias injection (documented in simulator code comments):** Young drivers draw `harsh_braking_count` from a distribution with mean 35% higher than senior drivers at equivalent speeds. This produces DIR ≈ 0.62 before correction — the seed of the entire AIF360 fairness demonstration. The bias is intentional and documented, not a data quality problem.

**Telemetry features per ping:** vehicle_id, driver_id, driver_age, timestamp, speed, engine_temp, oil_pressure, brake_wear_index, harsh_braking_count, rapid_acceleration_count, cornering_force, shift_type (day/night), GPS coordinates (Singapore bounding box)

**Synthetic complaint data (P4):** 200 complaints across 5 categories — driver conduct (35%), punctuality (25%), vehicle condition (20%), billing (12%), safety (8%). Language pattern variation to enable AIF360 language bias check.

**Synthetic maintenance history (P2):** 50 vehicles × 18 months of sensor readings, with labelled failure events. Known patterns: brake pads at 30K km, engine service at 10K km, tyre replacement at 50K km. Failure rate approximately 15% of records — class imbalance documented and addressed in model training.

---

## 12. Assessment Weight — Every Mark Accounted For

| Component                           | Weight   | Our Strategy                                                                       |
| ----------------------------------- | -------- | ---------------------------------------------------------------------------------- |
| Project Presentation                | 20%      | Open with cross-agent demo, show SHAP/LIME live in dashboard, 20 minutes rehearsed |
| Group Project Report                | 30%      | ~80 pages, all 9 sections, IMDA MAIGF + FEAT governance, before/after bias metrics |
| Individual Agent Design             | 13%      | 7-section template per member, deep technical design, justified decisions          |
| Individual Implementation & Testing | 13%      | Code walkthrough, test results with numbers, coverage by category                  |
| Individual Reflection               | 14%      | Personal, honest, names specific course lectures and concepts                      |
| Peer Assessment                     | 10%      | Clear ownership matrix, balanced contributions, everyone presents                  |
| **Total**                           | **100%** | Every percent mapped to a concrete deliverable                                     |

_"The best way to predict the future is to build it."_ _TraceData — AI intelligence that fleet operators already have the infrastructure for, and finally have the intelligence layer to use._
