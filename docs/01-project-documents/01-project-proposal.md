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

**Agent 1: Data Cleaner Gateway (ACL)**

- **Role:** Synchronously validates dual data sources: structured telemetry (GPS/speed) and unstructured text (appeals). Acts as an Anti-Corruption Layer (ACL).
- **Assurance:** Schema validation, range checks, offline detection.
- **Security:** SQL injection prevention, malicious payload rejection. Synchronously scrubs PII before domain routing.

**Agent 2: Deterministic Orchestrator (Central Router)**

- **Role:** Central dispatcher for complex Sagas. Uses deterministic logic (LangGraph decision trees) rather than open-ended LLM reasoning to route events based on payload types.
- **Autonomy:** Autonomous coordination of multi-step agent workflows.
- **Accountability:** Full audit trail for every routing decision and state transition.

**Agent 3: Behavior Evaluation Agent**

- **Role:** Scores trips (0-100) using predictive ML (XGBoost) and ensures fairness.
- **Fairness:** AIF360 bias detection + mitigation (Statistical Parity Difference < 0.2).
- **Explainability:** SHAP/LIME explanations for 100% of generated scores.
- **Accountability:** Feature importance tracked, bias correction logged.

**Agent 4: Driver Wellness Analyst Agent**

- **Role:** High-cohesion analyst for the Driver Profile context. Handles Sentiment, Advocacy, and Coaching within a single context window.
- **Personalization:** Coaching tone adapted based on emotional trajectory and safety performance.
- **Trust:** Processes driver appeals and listens to feedback to build advocacy.

**Agent 5: Safety Agent (Fast-Path)**

- **Role:** Detects critical incidents from Emergency Pings and executes multi-level interventions.
- **Assurance:** Real-time (< 500ms) incident detection bypassing background queues.
- **Accountability:** Incident logs + Fleet Manager escalation tracking.

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

| Priority     | Redis Channel          | Response                         | Examples                         |
| :----------- | :--------------------- | :------------------------------- | :------------------------------- |
| **critical** | emergency-critical     | Immediate Fleet Manager dispatch | collision, rollover              |
| **high**     | safety-high            | Real-time alert + coaching       | harsh_brake, vehicle_offline     |
| **medium**   | general-events         | Batched coaching                 | speeding                         |
| **low**      | analytics-low-priority | Analytics only                   | excessive_idle, normal_operation |

#### Technology Stack

| Component               | Framework/Library     | Rationale                                             |
| :---------------------- | :-------------------- | :---------------------------------------------------- |
| **Agent Orchestration** | LangGraph             | Deterministic state machine, cyclical routing         |
| **Fairness & Bias**     | AIF360 (IBM)          | Industry-standard fairness auditing, reweighting      |
| **Explainability**      | SHAP + LIME           | Feature importance (global + local)                   |
| **ML Model**            | XGBoost               | High-performance predictive modeling                  |
| **Async Framework**     | FastAPI               | Production-grade async Python framework               |
| **Task Queue**          | Celery + Redis 7      | Distributed task execution, priority queuing          |
| **Database**            | PostgreSQL + pgvector | Multi-schema context isolation, vector search         |
| **Messaging**           | Redis 7 Pub/Sub       | Event-Driven Architecture backbone (ADR 001)          |
| **LLM Integration**     | OpenAI / Google Gemini| Strategic reasoning + generative coaching             |
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
