# 🚛 TraceData — Master Plan for A+

## Intelligent Fleet Operations via Multi-Agent AI

**Team Size:** 4 members  
**Estimated Effort:** 15 days × 4 = 60 person-days  
**Target Grade:** A+

---

## 1. The Vision — Why Fleet Management?

Fleet management is a **goldmine** for multi-agent AI because it naturally decomposes into specialized domains that require autonomous decision-making, real-time coordination, and explainability for safety-critical operations. Unlike brand analytics (EchoChamber), fleet management involves:

- **Safety-critical decisions** — route choices, driver fatigue, vehicle health → explainability isn't optional, it's life-or-death
- **Real protected attributes** — driver demographics (age, gender, ethnicity) in performance scoring → genuine fairness/bias concerns
- **Rich adversarial surface** — GPS spoofing, telemetry tampering, prompt injection in chatbot → deep cybersecurity module coverage
- **Clear MLOps pipeline** — anomaly detection models that degrade over time → real model monitoring and retraining needs
- **Regulatory weight** — LTA (Singapore), PDPA for driver data, workplace safety regulations → governance frameworks apply naturally

**The Pitch:** TraceData is an AI-powered fleet intelligence platform that uses a multi-agent system to continuously monitor vehicle health, optimize routes, detect driver risk patterns, predict maintenance needs, ensure regulatory compliance, and provide conversational analytics access — all while maintaining explainability, fairness, and security across every decision.

---

## 2. The Agent Architecture — 8 Agents, 4 Owners

Each team member owns **2 agents** and writes a deep individual report on their **primary agent**.

### Agent Map & Ownership

| #   | Agent                                      | Primary Owner | Secondary Owner | Individual Report          |
| --- | ------------------------------------------ | ------------- | --------------- | -------------------------- |
| 1   | **Orchestrator Agent**                     | Member A      | —               | Member A writes about this |
| 2   | **Telemetry Ingestion Agent**              | Member A      | —               | —                          |
| 3   | **Route Optimizer Agent**                  | Member B      | —               | Member B writes about this |
| 4   | **Driver Behavior Agent**                  | Member B      | —               | —                          |
| 5   | **Predictive Maintenance Agent**           | Member C      | —               | Member C writes about this |
| 6   | **Compliance & Safety Agent**              | Member C      | —               | —                          |
| 7   | **Fleet Chatbot Agent (RAG)**              | Member D      | —               | Member D writes about this |
| 8   | **Sentinel Agent (Monitoring & Alerting)** | Member D      | —               | —                          |

### Why 8 Agents?

The briefing example (CARE-AI) uses 5 agents for a 4-5 person team. By having **8 well-scoped agents**, we:

- Give each member clear ownership of 2 agents
- Demonstrate richer multi-agent coordination patterns
- Show the lecturers we can handle complex orchestration
- Create more inter-agent communication surfaces to document

---

## 3. Agent Deep-Dive Designs

### Agent 1: Orchestrator Agent (Member A)

**Purpose:** Central coordinator that manages all workflow execution, routes incoming requests, handles agent failures, and maintains global state.

**Key Design Points:**

- Built with **LangGraph StateGraph** — directed acyclic graph with conditional edges
- Implements **parallel fan-out** (Telemetry + Route + Driver agents can run concurrently) and **fan-in** (Maintenance agent waits for Telemetry output)
- **Retry logic** with exponential backoff and circuit breaker pattern for agent failures
- **State machine visualization** — renders the current workflow state as a live diagram in the UI (this is XAI in action — the user can see _why_ the system is doing what it's doing)
- Maintains a **decision audit log** for every routing decision

**Reasoning Pattern:** Hierarchical planning — decomposes fleet manager requests into sub-tasks, assigns to agents, monitors completion, and aggregates results.

**Inter-Agent Protocol:** Defines a standard **AgentMessage** schema:

```
{
  "message_id": "uuid",
  "from_agent": "orchestrator",
  "to_agent": "route_optimizer",
  "intent": "optimize_routes",
  "payload": { ... },
  "priority": "high",
  "timestamp": "ISO8601",
  "trace_id": "uuid"  // for distributed tracing
}
```

---

### Agent 2: Telemetry Ingestion Agent (Member A)

**Purpose:** Collects, validates, and normalizes vehicle telemetry data (GPS, fuel, speed, engine diagnostics, tire pressure) from simulated IoT sources.

**Key Design Points:**

- **PII detection pipeline** — strips driver names, license plates, phone numbers from raw telemetry before processing (PDPA compliance)
- **Anomaly pre-screening** — flags impossible values (speed > 200km/h, negative fuel levels, GPS coordinates outside Singapore) using statistical bounds
- **Data quality scoring** — each telemetry batch gets a quality score; low-quality data is flagged for human review (Human-in-the-Loop from IMDA)
- Publishes clean data to shared state for downstream agents

**Reasoning Pattern:** Rule-based filtering + LLM-powered anomaly narration (turns raw anomalies into human-readable descriptions).

---

### Agent 3: Route Optimizer Agent (Member B)

**Purpose:** Generates optimal routes considering traffic, fuel efficiency, delivery windows, and driver constraints. Provides explainable route recommendations.

**Key Design Points:**

- Uses LLM to reason about multi-constraint optimization (time windows, driver hours, vehicle capacity, road restrictions)
- **Explainable routing** — every route recommendation includes a breakdown: "This route saves 12% fuel but adds 8 min. Chosen because driver X is approaching max driving hours." (XAI as a USER FEATURE, not just a test)
- **"Why not this route?"** — contrastive explanations. Users can ask why an alternative route was rejected
- **Fairness check** — ensures route assignments don't systematically disadvantage certain drivers (e.g., always giving senior drivers the easy routes)
- Integrates with external map APIs (simulated) for distance/time estimates

**Reasoning Pattern:** Chain-of-Thought with tool use — the LLM reasons step-by-step through constraints, calls tools for distance calculations, and produces a ranked route list with justifications.

**XAI Feature in UI:** A "Route Explanation" panel showing a SHAP-style breakdown of which factors influenced the route choice (distance weight: 30%, fuel weight: 25%, driver hours: 20%, delivery window: 25%).

---

### Agent 4: Driver Behavior Agent (Member B)

**Purpose:** Analyzes driver performance patterns — harsh braking, speeding, idle time, fatigue risk — and generates fair, explainable driver risk scores.

**Key Design Points:**

- **This is the fairness-critical agent** — driver scores directly affect job outcomes
- Implements **AIF360 fairness testing** on driver risk scores across protected attributes (age group, gender, experience level)
- **LIME explanations** for each driver score — "Driver X scored 72/100. Key factors: harsh braking events (+15 risk), excellent fuel efficiency (-8 risk), high idle time (+5 risk)"
- **Bias detection and correction** — if the model systematically scores younger drivers higher risk, apply reweighting or threshold adjustment (bias reduction from Module 1)
- **Human-Over-the-Loop** — flagged scores (very high or very low) are queued for human review before affecting driver records
- Fatigue detection using driving pattern analysis (time of day, continuous driving duration, deviation from normal patterns)

**Reasoning Pattern:** Hybrid — structured scoring formula (transparent, decomposable) + LLM narrative generation for manager-facing reports.

**XAI Feature in UI:** A "Driver Score Breakdown" dashboard with LIME waterfall charts showing positive/negative contributors. A "Fairness Dashboard" tab showing AIF360 metrics across demographic groups.

---

### Agent 5: Predictive Maintenance Agent (Member C)

**Purpose:** Predicts vehicle component failures before they occur, schedules preventive maintenance, and explains predictions to fleet managers.

**Key Design Points:**

- Uses a **classification model** (e.g., Random Forest or XGBoost) trained on simulated historical maintenance data — this gives us a proper ML model for SHAP/LIME, not just LLM wrapper
- **SHAP feature importance** — shows which telemetry features (engine temp trend, mileage since last service, vibration patterns) drive each prediction
- **Confidence intervals** — every prediction includes uncertainty: "78% probability of brake pad replacement needed within 2 weeks (±5 days)"
- **Model versioning with MLflow** — tracks model versions, training data versions, and performance metrics over time (MLSecOps)
- **Drift detection** — monitors if incoming telemetry distributions shift from training data, triggering retraining alerts
- Generates maintenance priority queues with cost-impact analysis

**Reasoning Pattern:** ML model for prediction + LLM for narrative explanation. The ML model produces the prediction; the LLM translates the SHAP values into natural language: "Engine overheating risk is high primarily because coolant temperature has trended upward 3°C over the past 2 weeks."

**XAI Feature in UI:** Interactive SHAP force plots for each vehicle's maintenance prediction. Fleet managers click a vehicle, see the prediction, and understand _exactly why_.

---

### Agent 6: Compliance & Safety Agent (Member C)

**Purpose:** Monitors regulatory compliance (driving hours, vehicle inspection schedules, license renewals) and safety incidents.

**Key Design Points:**

- **Rules engine** mapping Singapore LTA regulations + workplace safety requirements
- **Proactive alerting** — warns 7/14/30 days before compliance deadlines (license expiry, inspection due, COE renewal)
- **Incident classification** — when incidents occur, classifies severity and generates structured reports
- **Ethical decision log** — records every compliance decision with reasoning (aligned with IMDA MAIGF "Internal Governance Structures & Measures")
- **Escalation protocol** — critical safety issues (driver fatigue detected, vehicle brake failure predicted) trigger immediate human notification, bypassing normal workflow

**Reasoning Pattern:** Rule-based for regulatory checks + LLM for incident narrative generation and complex regulation interpretation.

---

### Agent 7: Fleet Chatbot Agent — RAG (Member D)

**Purpose:** Provides natural language query access to all fleet intelligence. Fleet managers ask questions like "Which vehicles are due for maintenance next week?" or "Show me Driver Lee's performance trend."

**Key Design Points:**

- **Hybrid RAG** — vector search (pgvector) + keyword search + structured SQL queries
- **Intent classification** with safety detection — routes queries to appropriate data sources
- **Multi-turn conversation** with anaphora resolution ("Show me his route history" → resolves "his" to previously discussed driver)
- **Defense-in-depth security:**
  - Layer 1: Regex pattern matching (prompt injection, SQL injection, XSS patterns)
  - Layer 2: LLM-based intent classification with `is_safe` flag and 10 boundary categories
  - Layer 3: OpenAI Moderation API for content safety
- **Source attribution** — every response cites the data source (which telemetry record, which maintenance log, which compliance rule)
- **"I don't know" honesty** — strict grounding prevents hallucination; if data doesn't exist, says so
- **Crisis protocol** — if a user query suggests an emergency ("truck is on fire"), immediately provides emergency contacts (SCDF 995)

**Reasoning Pattern:** Intent → Route → Retrieve → Ground → Respond → Cite. Each step logged for auditability.

**XAI Feature in UI:** Every chatbot response shows a "Sources" section with clickable links to the underlying data, plus a confidence indicator.

---

### Agent 8: Sentinel Agent — Monitoring & Alerting (Member D)

**Purpose:** The meta-agent that watches all other agents. Monitors system health, LLM costs, response quality, and compliance tracking.

**Key Design Points:**

- **LLM cost tracking** — real-time token usage and cost per agent, per query, per day
- **Performance metrics** — response latency P50/P95/P99, throughput, error rates
- **Quality scoring** — samples chatbot responses and scores them for relevance, groundedness, and safety
- **Compliance audit trail** — generates periodic compliance reports showing all agent decisions with timestamps, inputs, outputs, and reasoning
- **Alerting rules** — cost budget exceeded, latency spike, error rate above threshold, model drift detected
- **LangSmith integration** for distributed tracing across agent calls

**Reasoning Pattern:** Threshold-based monitoring + LLM for anomaly narration and alert summarization.

---

## 4. Module Coverage Matrix — Closing Every Gap

This is the **secret weapon**. We explicitly map every deliverable to the 4 course modules so the lecturers can see we've covered everything.

### Module 1: Explainable & Responsible AI (XRAI)

| Requirement                    | How We Cover It                                                          | Where (Agent/Section)                                     | EchoChamber Gap Closed?          |
| ------------------------------ | ------------------------------------------------------------------------ | --------------------------------------------------------- | -------------------------------- |
| **LIME explanations**          | Driver risk score keyword attribution                                    | Driver Behavior Agent — IN THE UI                         | ✅ XAI visible to users          |
| **SHAP explanations**          | Maintenance prediction feature importance                                | Predictive Maintenance Agent — IN THE UI                  | ✅ XAI visible to users          |
| **AIF360 fairness testing**    | Driver score fairness across age, gender, experience                     | Driver Behavior Agent — with before/after bias correction | ✅ Real bias found & fixed       |
| **Bias reduction**             | Reweighting or threshold adjustment on driver scores                     | Driver Behavior Agent                                     | ✅ Goes beyond EchoChamber       |
| **IMDA MAIGF alignment**       | Deep mapping across all 4 dimensions with evidence                       | Section 5 of report — detailed table                      | ✅ Deep, not surface-level       |
| **GenAI Governance Framework** | Map to the 9 dimensions (Accountability, Data, Trusted Dev, etc.)        | Section 5 of report                                       | ✅ NEW — EchoChamber missed this |
| **FEAT principles**            | Apply to driver scoring (Fairness, Ethics, Accountability, Transparency) | Driver Behavior Agent design                              | ✅ From reading list             |
| **Human-in-the-loop**          | Flagged driver scores, maintenance decisions requiring human approval    | Multiple agents                                           | ✅                               |
| **Contrastive explanations**   | "Why not Route B?" in Route Optimizer                                    | Route Optimizer Agent — IN THE UI                         | ✅ Advanced XAI technique        |
| **Ethical decision log**       | All agent decisions logged with reasoning                                | Compliance Agent + audit trail                            | ✅                               |

### Module 2: AI & Cybersecurity

| Requirement                         | How We Cover It                                       | Where                               |
| ----------------------------------- | ----------------------------------------------------- | ----------------------------------- |
| **STRIDE threat model**             | Structured threat analysis of entire system           | Section 6 — Risk Register skeleton  |
| **OWASP LLM Top 10**                | Map each risk to our agents with mitigations          | Section 6 — detailed table          |
| **Prompt injection defense**        | 3-layer defense (regex → LLM → Moderation API)        | Fleet Chatbot Agent                 |
| **Adversarial testing (Promptfoo)** | 400+ red-team tests                                   | Testing section                     |
| **Agent-to-agent security**         | Message signing, input validation between agents      | Architecture section — NEW          |
| **Data poisoning defense**          | Telemetry anomaly detection, training data validation | Telemetry Agent + Maintenance Agent |
| **Supply chain security**           | Dependency scanning in CI/CD (Snyk/Dependabot)        | MLSecOps pipeline                   |
| **PII protection**                  | Multi-layer PII detection in Telemetry Agent          | PDPA compliance                     |

### Module 3: Architecting Agentic AI Solutions

| Requirement                   | How We Cover It                                         | Where                      |
| ----------------------------- | ------------------------------------------------------- | -------------------------- |
| **Multi-agent architecture**  | 8 agents with clear roles                               | Agent Design section       |
| **Agent orchestration**       | LangGraph StateGraph with parallel fan-out/fan-in       | Orchestrator Agent         |
| **Agent autonomy**            | Each agent reasons, plans, and uses tools independently | Agent design docs          |
| **Inter-agent communication** | Explicit AgentMessage protocol + shared state           | Architecture section       |
| **Architecture patterns**     | Layered + Event-driven hybrid, justified                | System Architecture        |
| **Framework selection**       | LangGraph + LangChain, justify vs CrewAI/AutoGen        | Architecture justification |
| **Reference architecture**    | Logical + Physical architecture diagrams                | Section 3                  |

### Module 4: Integrating & Deploying AI Solutions

| Requirement           | How We Cover It                                                         | Where                        |
| --------------------- | ----------------------------------------------------------------------- | ---------------------------- |
| **CI/CD pipeline**    | GitHub Actions: lint → test → security scan → build → deploy            | MLSecOps section             |
| **MLSecOps**          | ML model versioning (MLflow), training data versioning, drift detection | Maintenance Agent + pipeline |
| **LLMSecOps**         | Prompt registry, LLM cost monitoring, output quality scoring            | Sentinel Agent + pipeline    |
| **Containerization**  | Docker + Docker Compose, deploy to AWS ECS or equivalent                | Deployment strategy          |
| **Automated testing** | Unit + Integration + Security + Fairness + XAI + Adversarial            | Testing section              |
| **Monitoring**        | LangSmith tracing + CloudWatch/Prometheus + custom dashboards           | Sentinel Agent               |
| **Model retraining**  | Drift detection → retrain trigger → validation → deploy                 | Maintenance Agent pipeline   |

---

## 5. Tech Stack

| Layer                | Technology                                                                              | Justification                                                 |
| -------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **Agent Framework**  | LangGraph + LangChain                                                                   | StateGraph for complex workflow orchestration; widely adopted |
| **LLM**              | OpenAI GPT-4o (analysis) + GPT-4o-mini (classification) + o3-mini (strategic reasoning) | Cost-optimized model routing                                  |
| **ML Model**         | XGBoost (maintenance prediction)                                                        | Interpretable, fast, works with SHAP natively                 |
| **Backend**          | FastAPI (Python)                                                                        | Async support, auto-generated API docs, lightweight           |
| **Frontend**         | Next.js + React                                                                         | Modern, SSR support, good charting ecosystem                  |
| **Database**         | PostgreSQL + pgvector                                                                   | Unified relational + vector search                            |
| **Task Queue**       | Celery + Redis                                                                          | Async agent execution, scheduled tasks                        |
| **ML Tracking**      | MLflow                                                                                  | Model versioning, experiment tracking, model registry         |
| **Monitoring**       | LangSmith + Prometheus + Grafana                                                        | LLM tracing + system metrics + dashboards                     |
| **CI/CD**            | GitHub Actions                                                                          | Integrated, free for open-source, good ecosystem              |
| **Deployment**       | Docker + AWS ECS Fargate                                                                | Serverless containers, no cluster management                  |
| **Security Testing** | Promptfoo + Bandit + Safety + Snyk                                                      | Adversarial + SAST + dependency scanning                      |
| **XAI**              | SHAP + LIME + AIF360                                                                    | Course-aligned, well-documented                               |

---

## 6. Work Breakdown & Timeline

Based on 15 days per person, ~60 person-days total. Briefing schedule: proposal by 18 Aug, project conduct 26 Aug–24 Oct, presentation 25 Oct/1 Nov, report by 17 Nov.

### Phase 1: Foundation (Week 1-2, ~16 person-days)

| Task                                               | Owner    | Days       |
| -------------------------------------------------- | -------- | ---------- |
| Set up repo, Docker, CI/CD skeleton, DB schema     | All      | 2 each = 8 |
| Design agent communication protocol & shared state | Member A | 2          |
| Set up LangGraph orchestration skeleton            | Member A | 2          |
| Simulated telemetry data generator                 | Member A | 2          |
| Frontend scaffold (Next.js + dashboard layout)     | Member D | 2          |

### Phase 2: Agent Implementation (Week 3-5, ~28 person-days)

| Task                                                                     | Owner    | Days |
| ------------------------------------------------------------------------ | -------- | ---- |
| Orchestrator Agent (workflow engine, state machine, retry logic)         | Member A | 4    |
| Telemetry Ingestion Agent (PII detection, validation, anomaly screening) | Member A | 3    |
| Route Optimizer Agent (LLM reasoning, constraint handling, explanations) | Member B | 4    |
| Driver Behavior Agent (scoring, LIME integration, fairness testing)      | Member B | 4    |
| Predictive Maintenance Agent (ML model, SHAP, MLflow integration)        | Member C | 4    |
| Compliance & Safety Agent (rules engine, incident classification)        | Member C | 3    |
| Fleet Chatbot Agent (RAG pipeline, 3-layer security, source attribution) | Member D | 4    |
| Sentinel Agent (monitoring, cost tracking, alerting)                     | Member D | 2    |

### Phase 3: Integration, Testing & Polish (Week 6-8, ~16 person-days)

| Task                                                  | Owner        | Days       |
| ----------------------------------------------------- | ------------ | ---------- |
| End-to-end integration testing                        | All          | 1 each = 4 |
| Promptfoo adversarial testing (400+ tests)            | Member D     | 2          |
| AIF360 fairness testing + bias correction             | Member B     | 2          |
| SHAP/LIME integration into UI                         | Member B + C | 2          |
| Security testing (STRIDE-based, OWASP LLM Top 10)     | Member C     | 2          |
| UI polish — XAI panels, dashboards, chatbot interface | Member D     | 2          |
| AWS deployment + CloudWatch setup                     | Member A     | 2          |

### Phase 4: Documentation & Presentation (Week 8-9)

| Task                                                            | Owner | Days |
| --------------------------------------------------------------- | ----- | ---- |
| Group report sections (each member writes their agent sections) | All   | —    |
| Individual reports (each member deep-dives their primary agent) | All   | —    |
| Presentation deck + demo rehearsal                              | All   | —    |

---

## 7. Deliverables Checklist (Aligned to Briefing Template)

### Group Report Structure

1. **Executive Summary** — project objective, solution highlights, constraints
2. **System Overview** — high-level workflow diagram showing all 8 agents
3. **System Architecture**
   - Logical architecture diagram (layered: Presentation → API Gateway → Orchestration → Business Logic → Data Access → Persistence)
   - Physical architecture diagram (AWS: VPC, ECS, RDS, ElastiCache, ALB, ECR, CloudWatch)
   - Deployment strategy (Docker, ECS Fargate, rolling deployments)
   - Data flow diagrams (telemetry pipeline flow, chatbot query flow, maintenance prediction flow)
   - Architecture justification (why LangGraph over CrewAI, why PostgreSQL+pgvector over Pinecone, etc.)
4. **Agent Roles and Design** — for each of the 8 agents:
   - Purpose & responsibilities
   - Reasoning patterns (CoT, ReAct, rule-based, hybrid)
   - Planning & memory mechanisms
   - Tools used
   - Communication protocols
   - Prompt engineering patterns
   - Fallback strategies
5. **Explainable & Responsible AI Practices** ⭐ THE DIFFERENTIATOR
   - Lifecycle alignment (data collection → processing → generation → monitoring)
   - **IMDA MAIGF v2** — deep mapping with evidence per dimension
   - **GenAI Governance Framework** — 9 dimensions mapped (Accountability, Data, Trusted Dev, Incident Reporting, Testing & Assurance, Security, Content Provenance, Safety & Alignment, AI for Public Good)
   - **FEAT principles** — applied to driver scoring
   - AIF360 fairness results with before/after bias correction narrative
   - LIME driver score explanations (with UI screenshots)
   - SHAP maintenance prediction explanations (with UI screenshots)
   - Contrastive route explanations
   - Ethical decision log
6. **AI Security Risk Register** ⭐ FRAMEWORK-DRIVEN
   - **STRIDE** threat model for the system
   - **OWASP LLM Top 10** mapping with mitigations
   - Comprehensive risk table (risk → severity → mitigation → control → test status)
   - Agent-to-agent security analysis
7. **MLSecOps / LLMSecOps Pipeline**
   - CI/CD architecture diagram
   - Automated testing framework (unit, integration, security, fairness, XAI, adversarial)
   - MLflow model versioning
   - Prompt registry and versioning
   - Deployment strategy with health checks
   - Monitoring & alerting (LangSmith + Prometheus + Grafana)
   - Logging & audit trail
8. **Testing Summary** — comprehensive table with test counts, pass rates, locations
9. **Reflection** — team-level learnings

### Individual Report Structure (per member)

1. Introduction — agent purpose
2. Agent Design — deep technical dive
3. Implementation Details — code structure, tech stack
4. Testing & Validation — with results
5. **Explainable & Responsible AI Considerations** — specific to this agent, citing course concepts by name
6. Security Practices — agent-specific risks and mitigations
7. **Reflection** — personal learning journey, honest about failures, explicit course concept connections ("In XRAI Day 2, we learned about LIME. I applied this when...")

---

## 8. The A+ Differentiators — What Sets Us Apart

These are the specific things we do that go beyond what EchoChamber did:

### 8.1 XAI as a User Feature (Not Just Tests)

- LIME waterfall charts in the Driver Performance dashboard
- SHAP force plots in the Vehicle Health dashboard
- "Why this route?" / "Why not Route B?" contrastive explanations
- Workflow state visualization in the Orchestrator
- Every chatbot response shows source citations with confidence

### 8.2 Real Bias Detection → Correction → Validation Cycle

- AIF360 testing finds that younger drivers are systematically scored higher risk
- Apply reweighting bias reduction technique
- Re-test with AIF360 to show improvement
- Document the entire journey with before/after metrics

### 8.3 Multi-Framework Governance (3 Frameworks, Not 1)

- IMDA MAIGF v2 (4 dimensions)
- GenAI Governance Framework (9 dimensions)
- FEAT principles (for driver scoring fairness)

### 8.4 STRIDE + OWASP LLM Top 10 Security Structure

- Not just Promptfoo categories, but mapped to established security frameworks
- Agent-to-agent security analysis (novel — not in EchoChamber)

### 8.5 Real ML Model with Full MLOps

- XGBoost for maintenance prediction — a proper ML model, not just LLM wrappers
- MLflow tracking, model versioning, drift detection
- This naturally demonstrates MLSecOps (Module 4) better than pure LLM systems

### 8.6 Personal, Course-Connected Reflections

- Each reflection names specific lectures and concepts
- Honest about what went wrong and how we pivoted
- Shows growth in thinking, not just technical output

### 8.7 Explicit Inter-Agent Communication Protocol

- Defined AgentMessage schema
- Sequence diagrams showing multi-agent coordination
- Communication pattern analysis (pub-sub, request-response, event-driven)

---

## 9. Risk Mitigation — What Could Go Wrong

| Risk                                            | Impact | Mitigation                                                                                         |
| ----------------------------------------------- | ------ | -------------------------------------------------------------------------------------------------- |
| Scope creep — 8 agents too ambitious            | HIGH   | Each agent has a MVP scope. Cut fancy features, keep core logic                                    |
| LLM API costs blow budget                       | MEDIUM | Aggressive mocking in tests, cost caps per agent, use GPT-4o-mini where possible                   |
| ML model doesn't perform well on simulated data | MEDIUM | Focus on XAI demonstration, not model accuracy. The point is showing SHAP/LIME, not winning Kaggle |
| Team member falls behind                        | HIGH   | Bi-weekly progress reports (required by briefing), clear ownership, agents are loosely coupled     |
| AWS deployment issues                           | MEDIUM | Have a Docker Compose local fallback for demo. Deploy early, not in the last week                  |
| Presentation runs over time                     | LOW    | Rehearse 3 times minimum. Each member presents their agents                                        |

---

## 10. Simulated Data Strategy

Since the project uses simulated data (explicitly allowed per the briefing), we need a realistic data generator:

- **Vehicle fleet:** 20-30 vehicles with different types (trucks, vans, sedans), ages, and maintenance histories
- **Driver pool:** 15-20 drivers with diverse demographics (age groups 25-60, mixed gender, varied experience levels) — essential for fairness testing
- **Telemetry streams:** GPS coordinates within Singapore, fuel levels, speed, engine temperature, brake events, idle time — generated at 1-minute intervals for 3 months
- **Maintenance records:** Historical maintenance events with component, cost, mileage — some with clear patterns (brake pads every 30K km) for the ML model to learn
- **Compliance records:** License expiry dates, vehicle inspection dates, driving hour logs
- **Inject some bias:** Deliberately make the simulated data slightly biased (younger drivers assigned to night shifts more often → more fatigue incidents) so we can detect and correct it with AIF360

---

## Quick Reference: Assessment Weight Mapping

| Assessment Component                    | Weight | Our Strategy                                                       |
| --------------------------------------- | ------ | ------------------------------------------------------------------ |
| **Project Presentation**                | 20%    | Clear slides, live demo of all 8 agents, XAI panels shown live     |
| **Group Project Report**                | 30%    | ~80-90 pages, every section from template, 3 governance frameworks |
| **Individual Agent Design**             | 10-13% | Deep dive per member's primary agent                               |
| **Individual Implementation & Testing** | 10-13% | Code walkthrough, test results, coverage                           |
| **Individual Reflection**               | 10-14% | Personal, honest, course-connected                                 |
| **Peer Assessment**                     | 10%    | Clear ownership, balanced contributions                            |

**Total: 100% — every percent accounted for.**

---

_"The best way to predict the future is to build it." — Let's build an A+._
