# 🚛 TraceData — Master Plan v2.1 (Scope-Optimized)

## Intelligent Fleet Operations via Multi-Agent AI

**Team Size:** 4 members  
**Total Effort:** ~45 person-days (realistic, with buffer)  
**Timeline:** 4 weeks (execution)  
**Date:** March 2026

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Why Fleet Management?](#2-why-fleet-management)
3. [Agent Architecture (Optimized Scope)](#3-agent-architecture-optimized-scope)
4. [System Design](#4-system-design)
5. [Implementation Timeline](#5-implementation-timeline)
6. [Module Coverage & Rubric Alignment](#6-module-coverage--rubric-alignment)
7. [Risk Mitigation](#7-risk-mitigation)
8. [Testing & Validation](#8-testing--validation)
9. [Deliverables & Assessment](#9-deliverables--assessment)
10. [References](#10-references)

## 1. Executive Summary

**TraceData** is an AI intelligence middleware system that attaches to existing truck fleet management infrastructure (TMS/FMS/ELD) to deliver predictive, explainable, and fair decision-making capabilities.

Fleet systems today handle **operational logging** efficiently (GPS tracking, basic hours recording) but lack **semantic reasoning**, **actionable explainability**, and **governance mechanisms**. TraceData bridges this "intelligence gap" by:

- **Ingesting real-time Kafka telemetry** (GPS, fuel, speed, engine diagnostics)
- **Deploying a lean, focused multi-agent system** (7 agents across 3 tiers)
- **Scoring driver behavior fairly** with bias detection & correction (AIF360)
- **Explaining every decision** visibly to users (SHAP, LIME, counterfactuals)
- **Maintaining strict observability** as platform infrastructure (audit logs, LangSmith tracing, cost tracking)
- **Ensuring human oversight** of critical decisions (HITL appeals, compliance review)

**Design Principle:** Execute with credibility. We commit to 4 core agents + 2 governance agents, all fully implemented and polished. Optional stretch goal: 1 visualization agent. No over-promising.

## 2. Why Fleet Management?

Fleet management is a **goldmine** for multi-agent AI because it naturally decomposes into specialized reasoning domains that require autonomous decision-making, real-time coordination, and explainability for safety-critical operations.

### Real-World Alignment

```mermaid
graph LR
    A["Fleet Management<br/>Real-World Problem"] --> B["Multi-Agent<br/>Decomposition"]
    B --> C1["Safety-Critical<br/>Decisions"]
    B --> C2["Protected<br/>Attributes"]
    B --> C3["Adversarial<br/>Surface"]
    B --> C4["MLOps<br/>Pipeline"]
    B --> C5["Regulatory<br/>Weight"]

    C1 --> D1["Explainability<br/>Non-Negotiable"]
    C2 --> D2["Fairness<br/>Real Bias Risk"]
    C3 --> D3["Cybersecurity<br/>Deep Coverage"]
    C4 --> D4["Model Monitoring<br/>& Retraining"]
    C5 --> D5["Governance<br/>Frameworks Apply"]

    D1 --> E["Maps to Module 1<br/>XRAI"]
    D2 --> E
    D3 --> F["Maps to Module 2<br/>Cybersecurity"]
    D4 --> G["Maps to Module 4<br/>MLSecOps"]
    D5 --> H["Maps to Module 3<br/>Agentic Reasoning"]

    style A fill:#e1f5ff
    style E fill:#c8e6c9
    style F fill:#ffe0b2
    style G fill:#f8bbd0
    style H fill:#e1bee7
```

## 3. Agent Architecture (Optimized Scope)

We build **7 agents across 3 tiers**, optimized for execution credibility while maintaining strong conceptual quality.

### 3.1 Tier 1: MUST (Core Backbone — 4 Agents)

**These four agents establish the minimal viable backbone that we _commit_ to fully implementing.** Observability and cost tracking are implemented as cross-cutting middleware services in the platform layer (satisfying Module 4 MLSecOps without adding agent complexity).

```mermaid
graph TD
    A["TIER 1: CORE BACKBONE<br/>4 Agents<br/>~16-20 person-days<br/>~4-5 days/person"]

    A --> B1["<b>1. Ingestion Engine</b><br/>Kafka → trip segments<br/>Schema validation<br/>Risk: 6.0/10"]
    A --> B2["<b>2. PII Cleaner</b><br/>Regex masking + jitter<br/>Deterministic (zero-LLM)<br/>Risk: 3.0/10"]
    A --> B3["<b>3. Driver Behaviour</b><br/>XGBoost + AIF360 + SHAP<br/>Core XRAI engine<br/>Risk: 6.5/10"]
    A --> B4["<b>4. Orchestrator</b><br/>LangGraph StateGraph<br/>Deterministic routing<br/>Risk: 7.5/10"]

    B1 --> C["✅ Module 4: Streaming"]
    B2 --> D["✅ Module 2: Security/Privacy"]
    B3 --> E["✅ Module 1: XRAI/Fairness"]
    B4 --> F["✅ Module 3: Agentic AI<br/>✅ Module 4: Observability"]

    style A fill:#ffcdd2
    style B1 fill:#ffebee
    style B2 fill:#ffebee
    style B3 fill:#ffebee
    style B4 fill:#ffebee
```

**Platform Observability (Infrastructure Layer, Not An Agent):**

- LangSmith tracing: Every LLM call instrumented
- Audit logging: Immutable decision log (satisfies IMDA accountability)
- Cost tracking: Token usage + latency P95 per agent
- Health checks: System alerts if any agent unhealthy

**Tier 1 Properties:**

- No inter-agent dependencies (Ingestion → PII → Orchestrator is the only critical path)
- Each agent can be tested in isolation
- Clear success criteria (data flows, fairness detected, system stable)
- Effort: ~4-5 days per person (very achievable, high confidence)

### 3.2 Tier 2: GOOD (Governance & Excellence — 2 Full + 2 PoCs)

**Given time and risk constraints, we will fully implement Compliance & Safety and RAG Assistant.** Actionable Recourse and Appeals Adjudicator will be explored as minimal PoCs to demonstrate conceptual understanding without over-committing implementation effort.

```mermaid
graph TD
    A["TIER 2: GOVERNANCE & EXCELLENCE"] --> B["2 FULL AGENTS<br/>~16-20 person-days"]
    A --> C["2 PROOF-OF-CONCEPT<br/>~4-6 person-days"]

    B --> B1["<b>1. Compliance & Safety</b><br/>Hybrid rules + LLM<br/>STRIDE threat model<br/>Risk: 6.5/10"]
    B --> B2["<b>2. RAG Assistant</b><br/>Conversational Q&A<br/>3-layer security<br/>Risk: 5.5/10"]

    C --> C1["<b>PoC: Actionable Recourse</b><br/>Simple counterfactual<br/>e.g. if harsh_braking -2 → score > threshold<br/>Risk: 4.0/10 for minimal version"]
    C --> C2["<b>PoC: Appeals Adjudicator</b><br/>Workflow documentation<br/>+ basic UI mockup<br/>Risk: 3.0/10"]

    B1 --> D["Module 2: Cybersecurity<br/>Module 3: Hybrid Reasoning"]
    B2 --> E["Module 2: Prompt Security<br/>IMDA Pillar 4:<br/>Stakeholder Interaction"]

    C1 --> F["Module 1: Fairness Recourse<br/>Shows understanding of<br/>Molnar/Barocas counterfactuals"]
    C2 --> G["Module 1: HITL Governance<br/>Shows understanding of<br/>IMDA accountability"]

    style A fill:#fff9c4
    style B1 fill:#fffde7
    style B2 fill:#fffde7
    style C1 fill:#ffccbc
    style C2 fill:#ffccbc
```

**2 Full Implementations:**

- **Compliance & Safety:** HOS rule engine + LLM reasoning for edge cases (weather delays, etc.) + STRIDE threat analysis
- **RAG Assistant:** Fleet manager Q&A ("Why did Driver 42 get low score?") + 3-layer security (regex → LLM → Moderation API) + source attribution

**2 PoCs (Conceptual Proof, Not Production):**

- **Actionable Recourse:** Simple counterfactual reasoning: "If harsh braking count reduced by 2, your score would cross the threshold." (Not full DiCE optimization)
- **Appeals Adjudicator:** Document the HITL workflow + create a basic UI mockup showing the decision flow (Not a fully automated system)

**Why this matters:**

- You still demonstrate understanding of fairness recourse and HITL governance
- But you're honest about implementation scope
- Graders respect focused execution over over-commitment
- Effort: 20-26 days total (~5-7 per person additional)

### 3.3 Tier 3: NICE (Stretch Goal — 1 Agent)

**If time and energy permit, we will implement Geo-Spatial Intelligence as a portfolio-quality feature.**

```mermaid
graph TD
    A["TIER 3: OPTIONAL STRETCH<br/>1 Agent<br/>~3-4 person-days if built"]

    A --> B["<b>Geo-Spatial Intelligence</b><br/>Heatmap: harsh-braking hotspots<br/>Privacy jittering (no individual tracking)<br/>Risk: 5.0/10"]

    B --> C["Module 1: Spatial XAI<br/>Portfolio appeal:<br/>Memorable demo visualization"]

    style A fill:#c8e6c9
    style B fill:#e8f5e9
```

**Why this agent specifically:**

- Visual (impressive in demo/interviews)
- Self-contained (doesn't block anything)
- Simple scope (map + clustering + jitter)
- Portfolio-ready quality

**Explicitly mark these as future work (bullets in conclusion):**

- Concept Drift monitoring
- Predictive Maintenance agent
- Anomaly Guard

### 3.4 Agent Dependency Graph (Critical Path)

```mermaid
graph TD
    A["📥 Ingestion Engine<br/>TIER 1 MUST"] -->|raw_telemetry| B["🔒 PII Cleaner<br/>TIER 1 MUST"]

    B -->|cleaned_data| C["🎯 Orchestrator<br/>TIER 1 MUST"]

    C -->|dispatch| D["⚖️ Driver Behaviour<br/>TIER 1 MUST<br/>XGBoost + AIF360 + SHAP"]

    C -->|dispatch| E["📋 Compliance & Safety<br/>TIER 2 FULL<br/>Rules + LLM"]

    D -->|risk_scores| F["💡 Actionable Recourse PoC<br/>TIER 2 PoC<br/>Simple counterfactual"]

    D -->|audit| G["✅ Appeals Adjudicator PoC<br/>TIER 2 PoC<br/>Workflow + mockup"]

    D -->|historical| H["🤖 RAG Assistant<br/>TIER 2 FULL<br/>Conversational Q&A"]

    G -->|appeal_context| H
    F -->|recourse_history| H

    A -->|location| I["🗺️ Geo-Spatial Intel<br/>TIER 3 STRETCH<br/>Heatmaps"]

    C -->|platform_level| J["⚙️ Platform Observability<br/>NOT AN AGENT<br/>LangSmith + Audit Log<br/>Cost Tracking"]

    style A fill:#ef5350,color:#fff
    style B fill:#ef5350,color:#fff
    style C fill:#ef5350,color:#fff
    style D fill:#ef5350,color:#fff

    style E fill:#fdd835,color:#000
    style H fill:#fdd835,color:#000

    style F fill:#ffccbc,color:#000
    style G fill:#ffccbc,color:#000

    style I fill:#81c784,color:#000

    style J fill:#b0bec5,color:#fff
```

**Critical Path (Week 1 blocker):**

- Ingestion (4 days) → PII (3 days) → Orchestrator (5 days) = 12 days total
- By end of Week 1, full pipeline working with mock data ✅

## 4. System Design

### 4.1 Architecture Diagram

```mermaid
graph TB
    subgraph "Data Layer"
        KAFKA["Kafka Stream<br/>Fleet Telemetry"]
        DB[("PostgreSQL<br/>+ pgvector<br/>Audit Logs")]
    end

    subgraph "Processing Layer"
        ING["Ingestion Engine<br/>Kafka Consumer"]
        PII["PII Cleaner<br/>Deterministic Masking"]
        ORCH["Orchestrator<br/>StateGraph Router"]
    end

    subgraph "Reasoning Layer"
        BEHAVIOR["Driver Behaviour<br/>XGBoost + SHAP"]
        COMPLIANCE["Compliance & Safety<br/>Rules + LLM"]
        RECOURSE["Actionable Recourse PoC<br/>Simple Counterfactual"]
    end

    subgraph "Platform Infrastructure"
        OBS["Observability Middleware<br/>LangSmith + Audit Log<br/>Cost Tracking"]
    end

    subgraph "User Interface"
        CHAT["RAG Assistant<br/>Conversational Q&A"]
        DASH["Fleet Dashboard<br/>XAI Visualizations"]
        MAP["Geo-Spatial Map<br/>Heatmaps (Stretch)"]
    end

    KAFKA --> ING
    ING --> PII
    PII --> ORCH
    ORCH --> BEHAVIOR
    ORCH --> COMPLIANCE
    BEHAVIOR --> RECOURSE
    BEHAVIOR --> DB
    COMPLIANCE --> DB
    RECOURSE --> CHAT
    ORCH --> OBS
    BEHAVIOR --> DASH
    CHAT --> DASH
    ING --> MAP

    style KAFKA fill:#e3f2fd
    style DB fill:#e3f2fd
    style ING fill:#ffebee
    style PII fill:#ffebee
    style ORCH fill:#ffebee
    style BEHAVIOR fill:#ffebee
    style COMPLIANCE fill:#fdd835
    style RECOURSE fill:#ffccbc
    style OBS fill:#b0bec5
    style CHAT fill:#fdd835
    style DASH fill:#f3e5f5
    style MAP fill:#c8e6c9
```

### 4.2 Technology Stack

| Layer                | Technology                 | Why                                                  |
| -------------------- | -------------------------- | ---------------------------------------------------- |
| **Agent Framework**  | LangGraph + LangChain      | StateGraph for orchestration; proven; widely adopted |
| **LLM**              | OpenAI GPT-4o-mini         | Cost-optimized, fast inference                       |
| **ML Model**         | XGBoost (Driver Behaviour) | Interpretable, native SHAP support                   |
| **Backend**          | FastAPI (Python)           | Async, lightweight, auto-docs                        |
| **Database**         | PostgreSQL + pgvector      | Unified relational + vector search                   |
| **XAI**              | SHAP + LIME + AIF360       | Course-aligned, production-ready                     |
| **Tracing**          | LangSmith                  | LLM observability, cost tracking                     |
| **Security Testing** | Promptfoo + Bandit         | Adversarial + SAST                                   |
| **Frontend**         | Next.js + React            | XAI dashboards, chatbot, maps                        |
| **Deployment**       | Docker + AWS ECS Fargate   | Serverless containers                                |
| **CI/CD**            | GitHub Actions             | Integrated testing + deployment                      |

---

## 5. Implementation Timeline

### 5.1 Realistic Gantt (45 Person-Days Total)

```mermaid
gantt
    title TraceData 4-Week Execution (Scope-Optimized)
    dateFormat YYYY-MM-DD

    section Week 1: Foundation
    Ingestion Engine (P2)           :ing, 2026-03-10, 4d
    PII Cleaner (P3)                :pii, 2026-03-10, 3d
    Orchestrator (Sree)             :orch, 2026-03-10, 5d

    section Week 2: Core + Governance
    Driver Behaviour (Sree)         :behavior, 2026-03-17, 8d
    Compliance & Safety (P3)        :compliance, 2026-03-17, 6d
    RAG Assistant (P4)              :rag, 2026-03-17, 5d

    section Week 3: PoCs + Stretch
    Actionable Recourse PoC (Sree)  :recourse, 2026-03-24, 2d
    Appeals PoC + UI (P4)           :appeals, 2026-03-24, 2d
    Geo-Spatial (stretch, P2)       :geo, 2026-03-24, 3d
    Integration Testing (All)       :integ, 2026-03-24, 2d

    section Week 4: Validation + Reports
    Adversarial Testing (P4)        :redteam, 2026-03-31, 1d
    Individual Reports (All)        :reports, 2026-03-31, 3d
    Demo Rehearsal + Final Polish   :demo, 2026-04-01, 1d
```

### 5.2 Detailed Phase Breakdown

#### **Phase 1: Foundation (Week 1) — ~15-16 person-days, ~4 days/person**

| Task                                         | Owner | Days   | Success Criteria                          |
| -------------------------------------------- | ----- | ------ | ----------------------------------------- |
| Kafka consumer + schema validation           | P2    | 4      | Telemetry flowing, schema validated       |
| PII masking + spatial jittering              | P3    | 3      | Raw → cleaned data verified, no PII leaks |
| LangGraph StateGraph + deterministic routing | Sree  | 5      | State machine works, routing tested       |
| GitHub repo + Docker Compose + local dev     | All   | 1 each | `docker-compose up` works                 |

**Week 1 Blocker Resolution:** Ingestion → PII → Orchestrator pipeline is live ✅

#### **Phase 2: Core & Governance (Week 2-3) — ~22-25 person-days, ~5-6 days/person**

| Task                                       | Owner | Days | Success Criteria                                             |
| ------------------------------------------ | ----- | ---- | ------------------------------------------------------------ |
| XGBoost model + AIF360 fairness testing    | Sree  | 4    | Model trains, bias detected (SPD > 0.10)                     |
| SHAP integration                           | Sree  | 2    | Feature importance computed                                  |
| Compliance rules engine (HOS, speed, rest) | P3    | 3    | Rules evaluate correctly                                     |
| Compliance LLM reasoning + guardrails      | P3    | 3    | Edge-case reasoning works, guardrails block unfair decisions |
| RAG pipeline (pgvector + semantic search)  | P4    | 2    | Retrieval works                                              |
| RAG security (3-layer defense)             | P4    | 2    | Prompt injection blocked                                     |
| RAG LLM generation                         | P4    | 1    | Bot answers questions correctly                              |

**Phase 2 Blocker Resolution:** Driver Behaviour + Compliance + RAG fully functional ✅

#### **Phase 3: PoCs + Stretch + Integration (Week 3) — ~10-12 person-days**

| Task                                            | Owner | Days | Success Criteria                                            |
| ----------------------------------------------- | ----- | ---- | ----------------------------------------------------------- |
| Actionable Recourse PoC (simple counterfactual) | Sree  | 2    | One example: "if harsh_braking -2, score crosses threshold" |
| Appeals Adjudicator PoC (workflow + UI mockup)  | P4    | 2    | Workflow documented, basic mockup created                   |
| Geo-Spatial heatmap (if energy)                 | P2    | 3    | Heatmap renders, privacy jitter applied                     |
| End-to-end integration testing                  | All   | 2    | Full pipeline works, no crashes                             |

---

#### **Phase 4: Validation & Reporting (Week 4) — ~8 person-days**

| Task                            | Owner | Days | Type                                      |
| ------------------------------- | ----- | ---- | ----------------------------------------- |
| Adversarial testing (Promptfoo) | P4    | 1    | >95% pass rate on 100+ tests              |
| Individual reports              | Each  | 2.5  | Deep design + implementation + reflection |
| Demo rehearsal + final polish   | All   | 0.5  | 5-min walkthrough, no crashes             |

### 5.3 Team Role Assignment (Explicit Commitment)

```mermaid
graph TB
    subgraph "TEAM ROLES"
        S["🧠 Sree<br/>Orchestration & Fairness Lead<br/>~13 days"]
        P2["📊 P2<br/>Data & Streaming Lead<br/>~7 days"]
        P3["🔐 P3<br/>Security & Compliance Lead<br/>~9 days"]
        P4["⚙️ P4<br/>Observability & UX Lead<br/>~11 days"]
    end

    subgraph "CORE AGENTS (Tier 1)"
        S1["Sree owns:<br/>Orchestrator<br/>Driver Behaviour"]
        P21["P2 owns:<br/>Ingestion Engine"]
        P31["P3 owns:<br/>PII Cleaner"]
    end

    subgraph "GOVERNANCE (Tier 2 Full)"
        P32["P3 owns:<br/>Compliance & Safety<br/>Risk model + hybrid reasoning"]
        P41["P4 owns:<br/>RAG Assistant<br/>Q&A + security + source attribution"]
    end

    subgraph "PoCs (Tier 2 Light)"
        S2["Sree explores:<br/>Actionable Recourse PoC<br/>Simple counterfactual"]
        P42["P4 explores:<br/>Appeals Adjudicator PoC<br/>Workflow + mockup"]
    end

    subgraph "INDIVIDUAL REPORTS"
        SR["Sree Reports:<br/>Driver Behaviour Agent<br/>Fairness spec + XRAI"]
        PR["P2 Reports:<br/>Ingestion Engine<br/>Data pipeline design"]
        CR["P3 Reports:<br/>PII Cleaner<br/>Security & privacy"]
        MR["P4 Reports:<br/>Platform Observability<br/>MLSecOps infrastructure"]
    end

    S --> S1
    P2 --> P21
    P3 --> P31
    P3 --> P32
    P4 --> P41

    S --> S2
    P4 --> P42

    S1 --> SR
    P21 --> PR
    P31 --> CR
    P32 --> MR

    style S fill:#bbdefb
    style P2 fill:#c8e6c9
    style P3 fill:#ffe0b2
    style P4 fill:#f8bbd0
```

**Effort Per Person:**

- **Week 1:** 3-4 days each (shared foundation)
- **Week 2-3:** 5-6 days each (core + governance + PoCs)
- **Week 4:** 1-2 days each (reporting + demo)
- **Total:** ~10-12 days per person ✅ **Realistic, achievable, with buffer**

## 6. Module Coverage & Rubric Alignment

### 6.1 Module 1: Explainable & Responsible AI

```mermaid
graph LR
    MOD1["Module 1: XRAI"] --> A["Bias Detection"]
    MOD1 --> B["Explainability"]
    MOD1 --> C["Fairness Recourse"]
    MOD1 --> D["Human Oversight"]

    A --> A1["AIF360 Testing<br/>Driver Behaviour<br/>Detect & correct bias"]
    B --> B1["SHAP Feature Importance<br/>Driver Behaviour<br/>Visible in UI"]
    B --> B2["LIME Local Explanations<br/>Waterfall charts"]
    C --> C1["Actionable Recourse PoC<br/>Simple counterfactual<br/>Shows conceptual understanding"]
    D --> D1["Appeals Adjudicator PoC<br/>HITL workflow doc<br/>Shows governance thinking"]

    style MOD1 fill:#c8e6c9
    style A1 fill:#a5d6a7
    style B1 fill:#a5d6a7
    style B2 fill:#a5d6a7
    style C1 fill:#fff9c4
    style D1 fill:#fff9c4
```

**Coverage:**

- ✅ Bias detection (AIF360: detect demographic bias in Driver Behaviour)
- ✅ Bias correction (reweighting or threshold adjustment)
- ✅ Fairness validation (SHAP: prove age importance dropped)
- ✅ Explainability (SHAP + LIME visible in dashboard)
- ✅ Fairness recourse (counterfactual PoC: show understanding of Molnar/Barocas)
- ✅ Human oversight (Appeals PoC: document HITL decision workflow)

### 6.2 Module 2: AI & Cybersecurity

```mermaid
graph LR
    MOD2["Module 2: Cybersecurity"] --> A["Data Privacy"]
    MOD2 --> B["Threat Modeling"]
    MOD2 --> C["Prompt Security"]

    A --> A1["PII Cleaner<br/>Regex + jitter<br/>PDPA compliance"]
    B --> B1["STRIDE Analysis<br/>Compliance Agent<br/>Threat register"]
    C --> C1["RAG 3-Layer Defense<br/>Regex → LLM → Moderation API"]

    style MOD2 fill:#ffe0b2
    style A1 fill:#ffcc80
    style B1 fill:#ffcc80
    style C1 fill:#ffcc80
```

**Coverage:**

- ✅ Data privacy (PII Cleaner: deterministic masking, PDPA)
- ✅ Threat modeling (Compliance Agent: STRIDE threat register)
- ✅ Prompt injection defense (RAG: 3-layer guards)

### 6.3 Module 3: Architecting Agentic AI

```mermaid
graph LR
    MOD3["Module 3: Agentic AI"] --> A["Orchestration"]
    MOD3 --> B["Hybrid Reasoning"]

    A --> A1["LangGraph StateGraph<br/>Orchestrator<br/>Parallel fan-out/fan-in"]
    B --> B1["Compliance Agent<br/>Rules + LLM<br/>Protected by guardrails"]

    style MOD3 fill:#f8bbd0
    style A1 fill:#f48fb1
    style B1 fill:#f48fb1
```

**Coverage:**

- ✅ Multi-agent coordination (Orchestrator routes to 6-7 agents)
- ✅ Parallel execution (asyncio for independent agents)
- ✅ Hybrid reasoning (Rules Engine + LLM in Compliance)
- ✅ State management (FleetState with checkpointing)

### 6.4 Module 4: MLSecOps

```mermaid
graph LR
    MOD4["Module 4: MLSecOps"] --> A["Real-Time Streaming"]
    MOD4 --> B["Cost & Observability"]
    MOD4 --> C["CI/CD Pipeline"]

    A --> A1["Kafka Ingestion<br/>Time-windowing<br/>Trip segments"]
    B --> B1["Platform Observability<br/>LangSmith tracing<br/>Audit logging<br/>Cost tracking"]
    C --> C1["GitHub Actions<br/>Lint → Test → Deploy"]

    style MOD4 fill:#bbdefb
    style A1 fill:#90caf9
    style B1 fill:#90caf9
    style C1 fill:#90caf9
```

**Coverage:**

- ✅ Real-time streaming (Kafka, time-windowing)
- ✅ Cost monitoring (platform observability middleware)
- ✅ Audit logging (immutable decision logs)
- ✅ CI/CD (automated testing + deployment gates)

## 7. Risk Mitigation

### 7.1 Risk Register (Scope-Optimized)

```mermaid
graph TD
    A["RISK REGISTER"] --> R1["MEDIUM: Actionable Recourse<br/>Now PoC (simpler risk)"]
    A --> R2["LOW: Team Pacing<br/>Clear ownership, realistic scope"]
    A --> R3["MEDIUM: LLM Cost<br/>Budget monitoring"]

    R1 --> R1M["MITIGATION:<br/>Simple counterfactual only<br/>No complex optimization<br/>2 days max<br/>Deliverable: one example + documentation"]

    R2 --> R2M["MITIGATION:<br/>4-person team, 4 core agents<br/>Each owns 1 agent<br/>Loosely coupled<br/>Bi-weekly syncs"]

    R3 --> R3M["MITIGATION:<br/>GPT-4o-mini for cost<br/>Aggressive testing mocks<br/>Cost caps per agent"]

    style A fill:#ffcdd2
    style R1 fill:#ffb74d
    style R2 fill:#81c784
    style R3 fill:#ffb74d
```

**Key principle:** By narrowing scope to 4 core + 2 full governance + 2 PoCs, we eliminate most risk while maintaining strong quality.

## 8. Testing & Validation

### 8.1 Testing Strategy

```mermaid
graph TB
    subgraph "Unit Testing"
        U1["Agent logic isolation<br/>Mocked inputs/outputs"]
        U2["Data validation<br/>PII masking, schema checks"]
        U3["Fairness detection<br/>AIF360 test cases"]
    end

    subgraph "Integration Testing"
        I1["End-to-end pipeline<br/>Telemetry → Score → Explanation"]
        I2["Inter-agent communication<br/>Message passing, state sync"]
    end

    subgraph "Security Testing"
        S1["Promptfoo: 100+ adversarial tests<br/>Prompt injection, bias amplification"]
        S2["SAST: Bandit<br/>Code security"]
    end

    subgraph "XAI Validation"
        X1["SHAP explanations<br/>Feature importance sensible"]
        X2["LIME local explanations<br/>Fidelity check"]
    end

    style U1 fill:#c8e6c9
    style U2 fill:#c8e6c9
    style U3 fill:#c8e6c9
    style I1 fill:#ffcc80
    style I2 fill:#ffcc80
    style S1 fill:#ef5350
    style S2 fill:#ef5350
    style X1 fill:#ce93d8
    style X2 fill:#ce93d8
```

## 9. Deliverables & Assessment

### 9.1 Group Report (80-90 Pages)

```mermaid
graph TD
    GR["Group Report"] --> S1["Executive Summary<br/>2 pages"]
    GR --> S2["System Overview<br/>3 pages"]
    GR --> S3["System Architecture<br/>8 pages"]
    GR --> S4["Agent Design<br/>7 agents explained<br/>20 pages"]
    GR --> S5["XRAI Practices<br/>15 pages"]
    GR --> S6["Cybersecurity<br/>Risk Register<br/>10 pages"]
    GR --> S7["MLSecOps<br/>8 pages"]
    GR --> S8["Testing<br/>5 pages"]
    GR --> S9["Conclusion & Future Work<br/>3 pages"]

    style GR fill:#e3f2fd
    style S1 fill:#bbdefb
    style S2 fill:#bbdefb
    style S3 fill:#90caf9
    style S4 fill:#90caf9
    style S5 fill:#64b5f6
    style S6 fill:#42a5f5
    style S7 fill:#42a5f5
    style S8 fill:#2196f3
    style S9 fill:#1976d2
```

### 9.2 Individual Reports

| Member   | Primary Agent          | Report Structure                                                                                            |
| -------- | ---------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Sree** | Driver Behaviour       | Design (fairness spec, AIF360) + Implementation (XGBoost, SHAP) + Reflection (XRAI learnings)               |
| **P2**   | Ingestion Engine       | Design (data pipeline, schema) + Implementation (Kafka, windowing) + Reflection (streaming learnings)       |
| **P3**   | PII Cleaner            | Design (privacy-first, deterministic) + Implementation (regex, jitter) + Reflection (security learnings)    |
| **P4**   | Platform Observability | Design (MLSecOps architecture) + Implementation (LangSmith, audit logs) + Reflection (governance learnings) |

**Each individual report:** ~8-10 pages

- Purpose & design (2-3 pages)
- Implementation (2-3 pages)
- Testing & validation (1-2 pages)
- XRAI/Cybersecurity/MLSecOps reflection (1-2 pages)
- Course concept connections (1 page)

## 10. References

[1] **IMDA Model AI Governance Framework (2nd Edition)**  
https://www.pdpc.gov.sg/Help-and-Resources/2020/01/Model-AI-Governance-Framework

[2] **Molnar, C. (2022). Interpretable Machine Learning**  
https://christophm.github.io/interpretable-ml-book/

[3] **Barocas, S., Hardt, M., Narayanan, A. (2023). Fairness and Machine Learning**  
https://fairmlbook.org/

[4] **LangGraph Documentation**  
https://langchain-ai.github.io/langgraph/

[5] **OWASP LLM Top 10**  
https://owasp.org/www-project-llm-ai-security-and-governance/

[6] **STRIDE Threat Modeling**  
https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool

[7] **AIF360: Fairness Toolkit**  
https://github.com/Trusted-AI/AIF360

[8] **SWE5008: Graduate Certificate in Architecting AI Systems (NUS-ISS)**

## Summary: Why This Works

| Factor                 | Before (9-11 agents)                                   | After (7 agents)                                       |
| ---------------------- | ------------------------------------------------------ | ------------------------------------------------------ |
| **Credibility**        | "We hope to..."                                        | "We commit to..."                                      |
| **Team Size Fit**      | 4 people building 11 agents = 2-3 each, thin execution | 4 people, 1-2 core agents each + shared work = focused |
| **Risk**               | High — slip on multiple agents                         | Low — execute well on core agents                      |
| **Module Coverage**    | All 4 modules fully covered                            | All 4 modules fully covered                            |
| **Quality**            | Conceptually strong, execution risk                    | Conceptually strong, execution credible                |
| **Grader Feeling**     | "Did they finish?"                                     | "They executed this well"                              |
| **Individual Reports** | Thin (3-4 pages per agent)                             | Deep (8-10 pages per agent)                            |

**"The difference between a good project and a great one isn't scope—it's execution credibility."**

This Master Plan v2.1 is ready to execute. You've kept strong conceptual elements while trimming to a scope 4 people can deliver with confidence.
