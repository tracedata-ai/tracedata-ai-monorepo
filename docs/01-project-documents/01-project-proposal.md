# TraceData: AI Intelligence Middleware for Fleet Management

**Content:** Title of the project.

## Project Sponsor

**Content:** Name, title, and contact (if applicable).

## Project Members

**Content:** Names of team members.

- Dinesh Punvasi Gupta
- Jenige Balachander
- Sreeraj Edakulathil Chellappan
- Zhicheng Yang

## Overview

**Content:** Describe the context and the business problem solved by the Agentic AI system.

### The Problem: 7 Critical Gaps in Current Fleet Telematics

Small-to-medium truck fleet operators (50-200 vehicles) currently use basic telematics (GPS + collision detection) but lack intelligent fleet management. Drivers face opaque scoring, no feedback, and no appeals mechanism. Current systems are having a penalizing effect on drivers which might result in demotivation, burnout and resignation. They fail on fairness, coaching, driver support, and transparency:

### Business Problem

1. **Unfair Scoring**: Rule-based systems penalize novice drivers without context, creating systematic bias that drives turnover (1)
2. **No Coaching**: Drivers receive scores but no personalized guidance; generic "drive safer" doesn't improve behavior (2)
3. **Missed Burnout**: Fleets detect stress only after incidents or resignations; no proactive wellbeing monitoring (3)
4. **No Appeals**: Drivers can't contest unfair scores, creating resentment and legal liability (4)
5. **Missing Context**: Scoring ignores environment (night, weather, road type), making comparisons unfair (5)
6. **Surveillance, Not Support**: Drivers see telematics as spyware; no transparency or privacy controls (6)
7. **Safety in Isolation**: Incident alerts don't account for driver's emotional state or workload (7)

### TraceData's Solution

7 autonomous agents that address all 7 gaps—fair scoring (AIF360), personalized coaching, burnout detection, appeals, contextual enrichment, private feedback, and integrated safety-welfare management.

### Core Philosophy
- **Fairness First**: Score adjustments should account for driver context, not penalize inexperience or unfortunate circumstances.
- **Driver-Centric**: The system empowers fleet managers to support drivers, not surveil them.
- **Transparent**: Every decision is observable and contestable.

## Scope of Work

**Content:** Describe the agents in your system. Define your scope of work, which must demonstrate key considerations such as assurance, trust, fairness, accountability, ethical issues, explainability, governance, security measures, agent autonomy and orchestration, as well as MLOps and LLMOps practices.

### Proposed High Level Architecture of Tracedata

#### Agents and Scope

**Agent 1: Ingestion Quality Agent**

- **Role:** Validates dual data sources: structured telemetry (GPS/speed) and unstructured text (appeals). Handles batched pings (4-10 min) vs real-time critical bypass.
- **Assurance:** Schema validation, range checks, offline detection
- **Fairness:** Equal treatment of all vehicles (no bias in ingestion)
- **Security:** SQL injection prevention, malicious payload rejection. Selectively routes only text to the PII Scrubber Agent.
- **Governance:** Data retention policy enforced

**Agent 2: Orchestrator Agent (Central Router)**

- **Powered by:** Hybrid (Deterministic Router + Small LLM)
- **Role:** Central dispatcher. Evaluates 4-minute batches quickly (discard/persist) or uses LLM reasoning to route unstructured text and manage driver encouragement profiles.
- **Trust & Accountability:** full audit trail for decisions made
- **Fairness:** Ensures fair agent utilization
- **Explainability:** Reasoning for every routing decision logged
- **Security:** Deterministic (90%) + semantic (10%) routing with fallbacks
- **Autonomy:** Autonomous decision-making for routing

**Agent 3: Behavior Agent**

- **Powered by:** XGBoost to rate the drivers trips out of 100, Fairness and XAI applied.
- **Role:** Scores trips (0-100), audits fairness
- **Fairness:** AIF360 bias detection + mitigation
- **Explainability:** LIME/SHAP explanations for every score
- **Accountability:** Feature importance tracked, bias correction logged
- **Security:** Adversarial input testing (data injection)
- **Ethical:** Fairness audit monthly

**Agent 4: Feedback and Advocacy Agent**

- **Powered by:** Embeds the feedback and appeals so that we can semantically search the data and enrich context (if needed) via LLM (Context Enrichment Agent)
- **Role:** Processes driver appeals, listens to feedback
- **Trust:** Appeals mechanism builds driver trust
- **Fairness:** Ensures drivers can contest unfair scores
- **Accountability:** All appeals logged with FM decisions
- **Explainability:** Provides reasoning for appeal responses
- **Ethics:** Driver-centric support, not surveillance

**Agent 5: Sentiment Agent**

- **Powered by:** Sentiment analysis on the written content (Fleet manager as well as Driver)
- **Role:** Tracks emotional trajectory, detects burnout
- **Accountability:** Burnout alerts logged, enables wellness interventions
- **Ethical:** Proactive driver support (not punitive)
- **Security:** Private emotional data encrypted, access controlled
- **Governance:** Burnout alerts escalate to FM with recommendations

**Agent 6: Coaching Agent**

- **Role:** Generates personalized coaching
- **Fairness:** Coaching tone matched to emotional state (not biased)
- **Explainability:** Coaching focuses on specific, addressable issues
- **Ethics:** Supportive, encouraging (not punitive)
- **Personalization:** Tone + content adapted per driver

**Agent 7: Safety Agent**

- **Powered by:** Dedicated high-priority Celery queue (Redis-backed) for Critical Events. Enriched via Context Agent.
- **Role:** Detects critical incidents and executes a multi-level intervention strategy: Level 1 (App Notification), Level 2 (Formal Message), Level 3 (Direct Call).
- **Assurance:** Real-time (< 5 sec) incident detection
- **Security:** Verification that critical event is real (not false alarm)
- **Accountability:** Incident log + FM action tracking
- **Governance:** Insurance compliance, regulatory reporting

**Agent 8: Context Enrichment Agent**

- **Powered by:** Model Context Protocol (MCP) to access external mapping and weather APIs deterministically within < 2 seconds.
- **Role:** Shared high-speed Tool providing road/weather context for decisions.
- **Fairness:** Context ensures fair comparisons (night vs day, urban vs highway)
- **Security:** Lookup integrity, no data leakage

#### Events and Categories

##### Event Categories (6 Semantic Groups)

| Category             | Events                                | Purpose                               | Escalation                              |
| :------------------- | :------------------------------------ | :------------------------------------ | :-------------------------------------- |
| **critical**         | collision, rollover, vehicle_offline  | Life-threatening or service-impacting | emergency_services, fleet_manager_alert |
| **harsh_events**     | harsh_brake, hard_accel, harsh_corner | Aggressive/unsafe driving behavior    | coaching                                |
| **speed_compliance** | speeding                              | Regulatory/compliance violation       | coaching                                |
| **idle_fuel**        | excessive_idle                        | Fuel efficiency concern               | coaching                                |
| **normal_operation** | normal_operation                      | Safe driving checkpoint               | analytics                               |
| **trip_lifecycle**   | start_of_trip, end_of_trip            | Trip boundaries                       | logging, ml_scoring                     |

##### Priority Levels (4 Operational Levels)

| Priority     | Celery Queue   | Response                         | Examples                         |
| :----------- | :------------- | :------------------------------- | :------------------------------- |
| **critical** | queue.critical | Immediate Fleet Manager dispatch | collision, rollover              |
| **high**     | queue.high     | Real-time alert + coaching       | harsh_brake, vehicle_offline     |
| **medium**   | queue.medium   | Batched coaching                 | speeding                         |
| **low**      | queue.low      | Analytics only                   | excessive_idle, normal_operation |

#### Technology Stack

| Component               | Framework/Library     | Rationale                                             |
| :---------------------- | :-------------------- | :---------------------------------------------------- |
| **Agent Orchestration** | LangGraph             | Autonomous agents as nodes, conditional routing       |
| **Fairness & Bias**     | AIF360 (IBM)          | Industry-standard fairness auditing, reweighting      |
| **Explainability**      | SHAP + LIME           | Feature importance (global + local)                   |
| **ML Model**            | XGBoost               | Fast, interpretable, handles missing data             |
| **Async Framework**     | FastAPI               | Production-grade async Python framework                                     |
| **Task Queue & Events** | Celery + Redis        | Priority queuing, event routing, async task execution, Redis Streams replay |
| **Database**            | PostgreSQL + pgvector | ACID compliance, JSONB, schema segregation per agent, vector search         |
| **ML Tracking**         | MLflow                | Model versioning, metrics logging                                           |
| **LLM Integration**     | OpenAI API            | Enrichment and Reasoning                              |
| **Type Safety**         | Pydantic              | Input validation, schema enforcement                  |
| **Testing**             | pytest                | Unit + integration tests, fixtures                    |
| **Monitoring**          | CloudWatch            | Metrics, logs, alarms                                 |
| **Containerization**    | Docker                | Environment consistency, scaling                      |

#### AI Security Risk Register & Guardrails
A comprehensive Risk Register (see *Section 5 of [03-project-report.md](./03-project-report.md)*) is maintained to mitigate AI-specific vulnerabilities, including:
- **Prompt Injection**: Mitigated via explicit templated prompts and string sanitization.
- **LLM Cost Explosion**: Mitigated via per-driver token/call quotas.
- **Fairness Drift**: Mitigated via monthly AIF360 automated audits and retraining loops.
- **Unauthorized Data Access**: Mitigated via RBAC and AES-256 encryption for private driver feedback.

## Effort Estimates

**Content:** List the rough Work Breakdown Structure (WBS) tasks and their estimated efforts, which ensures the team has thought about the approach and the implementation effort.

| Phase                    | Story Points (Per Person) |
| :----------------------- | :------------------------ |
| Phase 1 (Foundation)     | 2                         |
| Phase 2 (Core Agents)    | 5                         |
| Phase 3 (Support Agents) | 2                         |
| Phase 4 (Testing)        | 4                         |
| Phase 5 (Demo)           | 2                         |
| **TOTAL (x4 person)**    | **60**                    |
| **Per Person Average**   | **15**                    |

## References

1. Intellishift. (2024). How to Use Telematics to Improve Driver Behavior and Fleet Safety. Retrieved from https://intellishift.com/resources/featured-post/how-to-use-telematics-to-improve-driver-behavior-and-fleet-safety/ (Accessed: 9 March 2026).
2. Zenduit. (2024). Why Most Fleet Safety Programs Fail and How Coaching Can Fix It. Retrieved from https://zenduit.com/why-most-fleet-safety-programs-fail-and-how-coaching-can-fix-it/
3. Cameramatics. (2024). Truck Driver Health and Wellbeing: 6 Ways Fleet Managers Can Support Their Drivers. Retrieved from https://www.cameramatics.com/resources/truck-driver-health-and-wellbeing-6-ways-fleet-managers-can-support-their-drivers/
4. LinkedIn. How Telematics Data Can Predict Driver Resignations 30 Days in Advance. Retrieved from https://www.linkedin.com/pulse/how-telematics-data-can-predict-driver-resignations-30-days-d8wdc
5. Cartrack. (2024). Top 10 Fleet Management Mistakes and How to Avoid Them. Retrieved from https://www.cartrack.co.za/blog/top-10-fleet-management-mistakes-and-how-to-avoid-them
6. SafetyTrack. (2024). Telematics Implementation Mistakes: What Fleet Managers Should Know. Retrieved from https://www.safetytrack.com/blog/telematics-implementation-mistakes-what-fleet-managers-should-know/
7. Teletrac Navman. (2024). The Top 5 Challenges Fleet Operators Face and How Telematics Can Help. Retrieved from https://www.teletracnavman.com/fleet-management-software/telematics/resources/the-top-5-challenges-fleet-operators-face-and-how-telematics-can-help
