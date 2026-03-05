# 🚛 TraceData — Master Plan v2

**AI Intelligence Middleware for Fleet Management**

**SWE5008 Capstone Project | NUS-ISS Graduate Certificate in Architecting AI Systems**

**Team Size:** 4 members  
**Duration:** 4 weeks (26 Aug – 24 Oct)  
**Total Effort:** 50-55 person-days (~12-14 days per person)  
**Target Grade:** A+

---

## 1. Executive Summary

TraceData is an AI intelligence middleware system that attaches to existing fleet management infrastructure (TMS/FMS/ELD) to deliver **predictive, explainable, and fair decision-making capabilities** without requiring a rip-and-replace migration.

**The Problem:** Fleet systems handle operational logging (GPS, hours, fuel) but lack semantic reasoning, actionable explainability, and governance mechanisms.

**The Solution:** A multi-agent LangGraph system ingesting Kafka telemetry, detecting driver bias, predicting vehicle failures, ensuring regulatory compliance, and providing stakeholder-facing explanations—all with strict MLSecOps observability and IMDA MAIGF alignment.

**Key Differentiators Over EchoChamber:**

- ✅ **Actionable fairness recourse** (counterfactual coaching, not just detection)
- ✅ **Explicit HITL appeals process** (procedural fairness governance)
- ✅ **User-facing XAI** (LIME/SHAP in dashboards, not just tests)
- ✅ **3-framework governance** (IMDA MAIGF + GenAI Framework + FEAT)
- ✅ **Real ML model + MLOps** (XGBoost + MLflow, not pure LLM wrappers)

---

## 2. Agent Architecture — Tiered Prioritization

Based on the Architecturally Significant Requirements (ASR) framework, agents are prioritized by **operational credibility** (Tier 1), **excellence depth** (Tier 2), and **optional features** (Tier 3).

```mermaid
graph TB
    subgraph T1["TIER 1: MUST (Operational Credibility)"]
        O["🎯 Orchestrator<br/>Central Router<br/>7.5/10 complexity"]
        I["📥 Ingestion Engine<br/>Kafka Pipeline<br/>6.0/10 complexity"]
        D["⚖️ Driver Behaviour<br/>XRAI Core<br/>6.5/10 complexity"]
        P["🔒 PII Cleaner<br/>Privacy Checkpoint<br/>3.0/10 complexity"]
        C["💰 Cost & Monitoring<br/>MLSecOps Sentinel<br/>4.5/10 complexity"]
    end

    subgraph T2["TIER 2: GOOD (Excellence & Governance)"]
        A["💡 Actionable Recourse<br/>Counterfactual Coaching<br/>9.5/10 complexity - HIGH RISK"]
        CO["📋 Compliance & Safety<br/>Regulatory Engine<br/>6.5/10 complexity"]
        AP["✅ Appeals Adjudicator<br/>HITL Governance<br/>4.0/10 complexity"]
        R["🤖 RAG Assistant<br/>Stakeholder Chatbot<br/>5.5/10 complexity"]
    end

    subgraph T3["TIER 3: NICE (Stretch Goals)"]
        PM["🔧 Predictive Maint<br/>Secondary XAI<br/>7.0/10 complexity"]
        DR["📉 Concept Drift<br/>Model Monitoring<br/>7.0/10 complexity"]
        AN["🚨 Anomaly Guard<br/>Outlier Detection<br/>7.0/10 complexity"]
        GS["🗺️ Geo-Spatial Intel<br/>Visualization<br/>7.5/10 complexity"]
    end

    style T1 fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style T2 fill:#ffd93d,stroke:#f39c12,stroke-width:2px,color:#000
    style T3 fill:#a8d8ff,stroke:#3498db,stroke-width:2px,color:#000
```

### 2.1 Tier 1: MUST (5 Agents)

**Non-negotiable operational backbone. Satisfies baseline SWE5008 rubric.**

| Agent                 | Owner | Function                                                | ASR Impact      | Tech Diff | Notes                                                 |
| --------------------- | ----- | ------------------------------------------------------- | --------------- | --------- | ----------------------------------------------------- |
| **Orchestrator**      | Sree  | Multi-agent coordination via LangGraph StateGraph       | F🔴 Q🔴 C🔴 R🔴 | 7.5/10    | Central hub. Deterministic routing (no LLM overhead). |
| **Ingestion Engine**  | P2    | Kafka consumer + trip segment batching                  | F🔴 Q🔴 C🔴 R🟠 | 6.0/10    | Real-time streaming (Module 4 baseline).              |
| **Driver Behaviour**  | Sree  | XGBoost scoring + AIF360 fairness + SHAP explainability | F🔴 Q🔴 C🔴 R🔴 | 6.5/10    | Core XRAI engine (Module 1 proof point).              |
| **PII Cleaner**       | P3    | Deterministic regex masking + GPS jittering             | F🔴 Q🔴 C🔴 R🟡 | 3.0/10    | Privacy-first checkpoint (IMDA mandate).              |
| **Cost & Monitoring** | P4    | LangSmith tracing + audit logging + token cost tracking | F🔴 Q🔴 C🔴 R🟡 | 4.5/10    | MLSecOps observability (Module 4 core).               |

**Effort:** ~23 days (~6 days per person)  
**Critical Path:** Ingestion → PII → Orchestrator (5-6 days blocking)

---

### 2.2 Tier 2: GOOD (4 Agents)

**Excellence proof points. A+ differentiators. Safe to pick (depend on Tier 1).**

| Agent                   | Owner | Function                                                      | ASR Impact      | Tech Diff | Notes                                                                                      |
| ----------------------- | ----- | ------------------------------------------------------------- | --------------- | --------- | ------------------------------------------------------------------------------------------ |
| **Actionable Recourse** | Sree  | Counterfactual "what-if" coaching via Alibi/DiCE              | F🟠 Q🔴 C🟠 R🔴 | 9.5/10    | **HIGH RISK.** Week 1-2 prototype, go/no-go call. Fallback: deeper Driver Behaviour + RAG. |
| **Compliance & Safety** | P3    | Hybrid rules + LLM reasoning + STRIDE threat model            | F🟠 Q🔴 C🔴 R🟠 | 6.5/10    | Module 2 (cybersecurity) + Module 3 (hybrid agentic).                                      |
| **Appeals Adjudicator** | P4    | HITL workflow for disputed scores. Audit trail.               | F🟠 Q🔴 C🔴 R🟡 | 4.0/10    | IMDA procedural fairness pillar. Module 1 governance.                                      |
| **RAG Assistant**       | P4    | Conversational Q&A with source attribution + 3-layer security | F🟠 Q🟡 C🔴 R🟠 | 5.5/10    | IMDA Stakeholder Interaction pillar. User-facing XAI.                                      |

**Effort:** ~24 days (~6-7 additional days per person)  
**Dependency:** All safe to pick (depend only on Tier 1, which is guaranteed)

---

### 2.3 Tier 3: NICE (4 Agents)

**Secondary features. Stretch goals. Deferred without penalty.**

| Agent                 | Owner | Function                                          | Complexity | Notes                                                                |
| --------------------- | ----- | ------------------------------------------------- | ---------- | -------------------------------------------------------------------- |
| **Predictive Maint**  | P2    | ML failure prediction + SHAP explanations         | 7.0/10     | Redundant for rubric (XAI already in Driver Behaviour). Week 3 only. |
| **Concept Drift**     | P3    | Distribution shift monitoring + retraining alerts | 7.0/10     | Complementary to Cost & Monitoring. Optional.                        |
| **Anomaly Guard**     | P2    | Isolation Forest outlier detection                | 7.0/10     | Secondary defense. Optional.                                         |
| **Geo-Spatial Intel** | P4    | Heatmaps + privacy-preserving GPS aggregation     | 7.5/10     | Visualization polish. Optional.                                      |

**Effort:** ~28 days if all built (pick 0-1 max)

---

## 3. Agent Dependency Graph

```mermaid
graph TD
    A["📥 Ingestion Engine<br/>(TIER 1)"] -->|raw_telemetry| B["🔒 PII Cleaner<br/>(TIER 1)"]
    B -->|cleaned_data| C["🎯 Orchestrator<br/>(TIER 1)"]
    C -->|dispatch| D["⚖️ Driver Behaviour<br/>(TIER 1)"]
    C -->|dispatch| CO["📋 Compliance<br/>(TIER 2)"]
    C -->|all_calls| CM["💰 Cost & Monitoring<br/>(TIER 1)"]

    D -->|scores| AR["💡 Actionable Recourse<br/>(TIER 2)"]
    D -->|audit| AP["✅ Appeals<br/>(TIER 2)"]
    D -->|history| R["🤖 RAG<br/>(TIER 2)"]
    AR -->|recourse_history| R
    AP -->|appeal_context| R

    D -->|drift_metrics| DR["📉 Concept Drift<br/>(TIER 3)"]
    A -->|sensor_data| PM["🔧 Pred Maint<br/>(TIER 3)"]
    A -->|location| GS["🗺️ Geo-Spatial<br/>(TIER 3)"]
    B -->|quality| AN["🚨 Anomaly<br/>(TIER 3)"]

    style A fill:#ff6b6b,color:#fff
    style B fill:#ff6b6b,color:#fff
    style C fill:#ff6b6b,color:#fff
    style D fill:#ff6b6b,color:#fff
    style CM fill:#ff6b6b,color:#fff

    style AR fill:#ffd93d,color:#000
    style CO fill:#ffd93d,color:#000
    style AP fill:#ffd93d,color:#000
    style R fill:#ffd93d,color:#000

    style PM fill:#a8d8ff,color:#000
    style DR fill:#a8d8ff,color:#000
    style AN fill:#a8d8ff,color:#000
    style GS fill:#a8d8ff,color:#000
```

### Key Insights

- **Hard dependencies:** Ingestion → PII → Orchestrator only
- **All other agents** depend on Tier 1 (safe to parallelize Week 2)
- **Tier 3 agents** have zero downstream dependencies (can be deferred)
- **Driver Behaviour** is the bottleneck (5 agents depend on it, but it only depends on Orchestrator)

---

## 4. Implementation Timeline

```mermaid
gantt
    title TraceData 4-Week Sprint
    dateFormat YYYY-MM-DD

    section Week 1: Infra
    Ingestion Engine           :ing, 2024-08-26, 4d
    PII Cleaner                :pii, after ing, 3d
    Orchestrator Skeleton      :orch, after pii, 5d
    Cost & Monitoring Setup    :mon, after orch, 4d

    section Week 2: Intelligence
    Driver Behaviour           :db, 2024-09-02, 8d
    Compliance & Safety        :comp, after orch, 6d
    RAG Assistant              :rag, after db, 5d
    Appeals Adjudicator        :app, after db, 4d
    Actionable Recourse Prototype :ar_proto, after db, 5d

    section Week 3: Polish
    Actionable Recourse Full   :ar_full, after ar_proto, 3d
    Integration Testing        :test, after ar_full, 2d
    UI Polish & XAI Panels     :ui, after test, 2d
    Red-Team CI/CD Tests       :red, after ui, 2d

    section Week 4: Reporting
    Individual Reports         :ind, 2024-09-23, 4d
    Group Report               :grp, after ind, 3d
    Demo Rehearsal             :demo, after grp, 2d
```

### Phase Breakdown

```mermaid
graph LR
    P1["PHASE 1<br/>Week 1<br/>Infrastructure<br/>~16 days<br/>~4/person"] -->|Tier 1 Ready| P2["PHASE 2<br/>Weeks 2-3<br/>Intelligence<br/>~33 days<br/>~8-9/person"]
    P2 -->|Core Complete| P3["PHASE 3<br/>Week 4<br/>Validation<br/>~8 days<br/>Shared"]

    style P1 fill:#ff6b6b,color:#fff
    style P2 fill:#ffd93d,color:#000
    style P3 fill:#a8d8ff,color:#000
```

---

## 5. Team Ownership & Individual Reports

```mermaid
graph TB
    subgraph Sree["Sree (Behavior & Orchestration Lead)"]
        SO["Owns: Orchestrator"]
        SD["Owns: Driver Behaviour"]
        SA["Owns: Actionable Recourse"]
        SR["Individual Report:<br/>Driver Behaviour Design<br/>(fairness spec + XRAI proof)"]
    end

    subgraph P2["P2 (Data & Streaming Lead)"]
        SI["Owns: Ingestion Engine"]
        SPM["Owns: Predictive Maint (stretch)"]
        SR2["Individual Report:<br/>Ingestion Architecture<br/>(data pipeline design)"]
    end

    subgraph P3["P3 (Security & Privacy Lead)"]
        SP["Owns: PII Cleaner"]
        SC["Owns: Compliance & Safety"]
        SR3["Individual Report:<br/>Security/Privacy Checkpoint<br/>(STRIDE + threat model)"]
    end

    subgraph P4["P4 (MLSecOps & Governance Lead)"]
        SM["Owns: Cost & Monitoring"]
        SRA["Owns: RAG Assistant"]
        SAP["Owns: Appeals Adjudicator"]
        SR4["Individual Report:<br/>Observability & HITL Governance<br/>(MLSecOps + audit trail)"]
    end

    style Sree fill:#ff6b6b,color:#fff
    style P2 fill:#a8d8ff,color:#000
    style P3 fill:#a8d8ff,color:#000
    style P4 fill:#a8d8ff,color:#000
```

| Owner    | Primary Agent     | Secondary Agents                  | Effort   | Individual Report Focus                                 |
| -------- | ----------------- | --------------------------------- | -------- | ------------------------------------------------------- |
| **Sree** | Driver Behaviour  | Orchestrator, Actionable Recourse | ~18 days | Fairness specification (AIF360 + SHAP + Module 1 proof) |
| **P2**   | Ingestion Engine  | Predictive Maint (stretch)        | ~9 days  | Data pipeline architecture (streaming + schema)         |
| **P3**   | PII Cleaner       | Compliance & Safety               | ~9 days  | Security checkpoint design (STRIDE threat model)        |
| **P4**   | Cost & Monitoring | RAG, Appeals                      | ~13 days | Observability & governance (audit logging + HITL)       |

---

## 6. SWE5008 Rubric Coverage (Per Module)

```mermaid
graph TB
    subgraph Mod1["Module 1: XRAI"]
        M1A["✅ Bias Detection (AIF360)"]
        M1B["✅ Explainability (SHAP/LIME)"]
        M1C["✅ Fairness Recourse (Actionable)"]
        M1D["✅ Human Oversight (Appeals)"]
    end

    subgraph Mod2["Module 2: Cybersecurity"]
        M2A["✅ Data Privacy (PII Cleaner)"]
        M2B["✅ Threat Modeling (STRIDE)"]
        M2C["✅ Adversarial Testing (Promptfoo CI/CD)"]
        M2D["✅ Prompt Injection Defense (RAG)"]
    end

    subgraph Mod3["Module 3: Agentic AI"]
        M3A["✅ Multi-Agent Orchestration (LangGraph)"]
        M3B["✅ Tool Use & Planning (Compliance hybrid)"]
        M3C["✅ State Management (FleetState)"]
        M3D["✅ Proactive Agency (RAG, Recourse)"]
    end

    subgraph Mod4["Module 4: MLSecOps"]
        M4A["✅ Streaming (Ingestion Engine)"]
        M4B["✅ Observability (Cost & Monitoring)"]
        M4C["✅ Audit Logging (Decision Log)"]
        M4D["✅ Model Monitoring (Concept Drift)"]
    end

    IMDA["IMDA MAIGF<br/>4 Pillars"]
    M1D --> IMDA
    M1C --> IMDA
    M2A --> IMDA
    M4C --> IMDA

    style Mod1 fill:#ff6b6b,color:#fff
    style Mod2 fill:#ff6b6b,color:#fff
    style Mod3 fill:#ff6b6b,color:#fff
    style Mod4 fill:#ff6b6b,color:#fff
    style IMDA fill:#ffd93d,color:#000
```

**Coverage:** All 4 modules fully satisfied by Tier 1 + Tier 2 agents. Tier 3 adds optional depth.

---

## 7. Risk Mitigation

### Actionable Recourse (The Wild Card)

```mermaid
graph TD
    START["Week 1-2<br/>Prototype Alibi/DiCE<br/>on toy data"] --> DECISION{Works<br/>cleanly?}

    DECISION -->|YES| COMMIT["Commit to full implementation<br/>Week 2-3"]
    DECISION -->|NO| PIVOT["Pivot: Deeper Driver Behaviour<br/>+ RAG explainability<br/>(Still A-grade)"]

    COMMIT --> DEMO1["Live demo:<br/>Counterfactual coaching"]
    PIVOT --> DEMO2["Live demo:<br/>SHAP/LIME explanations<br/>+ Appeals workflow"]

    DEMO1 --> RESULT["A+ Proof:<br/>Fairness is actionable"]
    DEMO2 --> RESULT["A Proof:<br/>Fairness is explainable<br/>+ governable"]

    style START fill:#ffd93d,color:#000
    style DECISION fill:#ff6b6b,color:#fff
    style COMMIT fill:#90EE90,color:#000
    style PIVOT fill:#90EE90,color:#000
    style RESULT fill:#90EE90,color:#000
```

**Execution Strategy:**

1. **Week 1 Day 4-5:** Sree prototypes Alibi/DiCE with 3-5 toy drivers
2. **Week 2 Day 1:** Go/no-go decision call (team sync)
3. **If GO:** Full implementation Week 2-3
4. **If NO-GO:** Sree pivots to deepening Driver Behaviour + RAG (test contrastive explanations, fairness sandboxes)

**Outcome:** Either way, A-grade minimum guaranteed.

---

### Other Risks

| Risk                                | Severity | Mitigation                                                                                                   |
| ----------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------ |
| Scope creep (8→13 agents feels big) | HIGH     | Each agent has MVP scope. Cut fancy features, keep core logic. Tier 1 is non-negotiable; Tier 2/3 are picks. |
| LLM API costs                       | MEDIUM   | Aggressive mocking in tests. Cost caps per agent. Use GPT-4o-mini where possible.                            |
| Team member falls behind            | HIGH     | Bi-weekly progress reports. Clear ownership. Agents are loosely coupled (can be built independently).        |
| AWS deployment issues               | MEDIUM   | Docker Compose local fallback for demo. Deploy early (Week 3), not last minute.                              |
| ML model doesn't perform well       | MEDIUM   | Focus on XAI (SHAP/LIME), not accuracy. The proof point is interpretability, not Kaggle medals.              |

---

## 8. Pre-Deployment Adversarial Testing (CI/CD)

Adversarial testing is handled in GitHub Actions, **not as a runtime agent**, to reduce architectural complexity while proving Module 2 competency.

```mermaid
graph LR
    subgraph CI/CD["GitHub Actions Workflow"]
        T1["Test 1<br/>Prompt Injection<br/>on RAG"]
        T2["Test 2<br/>Bias Amplification<br/>alter age"]
        T3["Test 3<br/>Privacy Leakage<br/>PII masks"]
        T4["Test 4<br/>Fairness Jailbreak<br/>force unfair"]
    end

    CI/CD --> GATE{"Pass Rate<br/>>95%?"}
    GATE -->|YES| DEPLOY["✅ Deploy to AWS"]
    GATE -->|NO| BLOCK["❌ Block Deployment<br/>Fix & Retry"]

    style CI/CD fill:#a8d8ff,color:#000
    style GATE fill:#ffd93d,color:#000
    style DEPLOY fill:#90EE90,color:#000
    style BLOCK fill:#ff6b6b,color:#fff
```

**Acceptance Criteria:** >95% pass rate (matches EchoChamber baseline)

---

## 9. Live Demo Scenario (Week 4, ~5 Minutes)

```mermaid
sequenceDiagram
    participant Sree
    participant Driver Behaviour
    participant AIF360
    participant SHAP
    participant P4
    participant RAG
    participant Appeals

    Sree->>Driver Behaviour: "Score Driver X (age 25)"
    Driver Behaviour->>AIF360: Check fairness (SPD metric)
    AIF360-->>Driver Behaviour: SPD=0.38 (unfair - younger penalized)
    Driver Behaviour->>AIF360: Apply reweighting mitigation
    AIF360-->>Driver Behaviour: Retrain, SPD=0.04 (fair)

    Sree->>SHAP: Show feature importance before/after
    SHAP-->>Sree: Age importance: 45% → 12% (proved correction worked)

    Sree->>Driver Behaviour: Generate score narrative
    Driver Behaviour-->>Sree: "Driver X scored 68 due to speed variance, not age"

    P4->>RAG: Fleet manager asks "Why Driver X low score?"
    RAG->>Driver Behaviour: Retrieve historical scores + explanations
    RAG-->>P4: "Speed variance detected 3× in past month"

    P4->>Appeals: Driver disputes. Log for human review
    Appeals-->>P4: Decision audit trail recorded

    Sree->>Sree: Graders see: Architecture works, fairness is detectable/correctable/explainable, governance is auditable
```

**Talking Points:**

- Statistical Parity Difference metric (Module 1)
- AIF360 reweighting (fairness correction, not just detection)
- SHAP validation (explainability proves correction worked)
- User-facing RAG explanation (IMDA Stakeholder Interaction)
- Appeals audit trail (procedural fairness governance)

---

## 10. Deliverables Checklist

```mermaid
graph TB
    subgraph GRP["Group Report<br/>~80-90 pages"]
        G1["Executive Summary<br/>+ System Overview"]
        G2["System Architecture<br/>(logical + physical)"]
        G3["Agent Roles & Design<br/>(all 8 agents)"]
        G4["XRAI Deep-Dive<br/>(AIF360 + SHAP + LIME)"]
        G5["Security Register<br/>(STRIDE + OWASP LLM)"]
        G6["MLSecOps Pipeline<br/>(CI/CD + monitoring)"]
        G7["Testing Summary<br/>(with pass rates)"]
        G8["Reflection"]
    end

    subgraph IND["Individual Reports<br/>Per person"]
        I1["Agent Design<br/>(technical deep-dive)"]
        I2["Implementation<br/>(code structure)"]
        I3["Testing & Validation"]
        I4["XRAI Considerations<br/>(course-specific)"]
        I5["Security Practices"]
        I6["Personal Reflection<br/>(honest, course-connected)"]
    end

    subgraph PRES["Presentation<br/>Week 4"]
        P1["Slides<br/>(clear, structured)"]
        P2["Live Demo<br/>(5-7 min walkthrough)"]
        P3["Q&A Ready<br/>(hard questions prep)"]
    end

    style GRP fill:#ff6b6b,color:#fff
    style IND fill:#ffd93d,color:#000
    style PRES fill:#a8d8ff,color:#000
```

---

## 11. Assessment Weight & Grade Mapping

```mermaid
graph TB
    subgraph Grading["SWE5008 Assessment"]
        PRE["Project Presentation<br/>20%"]
        GRP["Group Report<br/>30%"]
        AGN["Agent Design<br/>10-13%"]
        IMP["Implementation<br/>10-13%"]
        REF["Individual Reflection<br/>10-14%"]
        PEA["Peer Assessment<br/>10%"]
    end

    STRATEGY["Our Strategy"]

    PRE --> STRAT1["Live demo shows all tiers<br/>XAI panels visible"]
    GRP --> STRAT2["3 governance frameworks<br/>80-90 pages comprehensive"]
    AGN --> STRAT3["Deep fairness spec<br/>per Sree's report"]
    IMP --> STRAT4["Code walkthrough<br/>test coverage"]
    REF --> STRAT5["Personal, honest<br/>course-connected"]
    PEA --> STRAT6["Clear ownership<br/>balanced work"]

    style PRE fill:#ff6b6b,color:#fff
    style GRP fill:#ff6b6b,color:#fff
    style AGN fill:#ffd93d,color:#000
    style IMP fill:#ffd93d,color:#000
    style REF fill:#a8d8ff,color:#000
    style PEA fill:#a8d8ff,color:#000
```

**Mapping:** Every assessment component has a clear TraceData proof point.

---

## 12. The EchoChamber Comparison

```mermaid
graph LR
    subgraph EC["EchoChamber Analyst<br/>(Reference A+)"]
        ECF["Fairness detection<br/>(AIF360)"]
        ECX["Explainability<br/>(LIME/SHAP)"]
        ECC["Compliance logging<br/>(audit trail)"]
        ECS["System design<br/>(clean, modular)"]
    end

    subgraph TR["TraceData<br/>(Our Goal)"]
        TRF["+ Fairness RECOURSE<br/>(counterfactual coaching)"]
        TRH["+ HITL Appeals<br/>(procedural fairness)"]
        TRU["+ User-facing XAI<br/>(RAG explanations)"]
        TRG["+ 3 Governance Frameworks<br/>(IMDA + GenAI + FEAT)"]
    end

    ECF -.-> TRF
    ECX -.-> TRU
    ECC -.-> TRH
    ECS -.-> TRG

    style EC fill:#a8d8ff,color:#000
    style TR fill:#90EE90,color:#000
```

**Key Improvement:** We don't just detect bias; we help drivers improve.

---

## 13. Key Dates & Milestones

```mermaid
timeline
    title Project Timeline

    2024-08-18 : Proposal Submission
    2024-08-26 : Week 1 Kickoff - Tier 1 infra starts
    2024-09-02 : Week 2 - Driver Behaviour ready, Tier 2 starts
    2024-09-09 : Week 3 - Polish & integration testing
    2024-09-16 : Week 4 - Red-team tests, reports
    2024-09-23 : Individual reports due
    2024-09-30 : Group report due
    2024-10-01 : Presentation & Live Demo
    2024-10-17 : Final report deadline
```

---

## 14. Success Criteria (A+ Outcome)

| Dimension               | A+ Proof                                    | Our Strategy                                                 |
| ----------------------- | ------------------------------------------- | ------------------------------------------------------------ |
| **Rubric Mastery**      | All 4 modules + IMDA covered                | Explicit mapping table. Every agent touches 1-2 modules.     |
| **System Quality**      | Working end-to-end pipeline                 | Tier 1 guaranteed; Tier 2 optional but likely.               |
| **XRAI Excellence**     | Fairness is actionable, not just detectable | Actionable Recourse (if viable) or Appeals + RAG (fallback). |
| **Security Rigor**      | STRIDE + OWASP systematically addressed     | Risk register. CI/CD red-team tests >95% pass.               |
| **Governance Maturity** | Audit trail, HITL, source attribution       | Appeals + Cost & Monitoring + RAG source links.              |
| **XAI in Practice**     | Users see explanations in real time         | LIME/SHAP panels in dashboards. RAG cites sources.           |
| **Honest Reflection**   | Learning, not just technical output         | Individual reports name specific lectures + concepts.        |

---

## 15. Quick Start (Week 1 Day 1)

1. **GitHub repo setup** (fork template, folder structure)
2. **Dev environment** (Python 3.11, PostgreSQL 15, Redis, Docker Compose)
3. **Kafka simulator** (Python producer, toy telemetry generator)
4. **LangGraph skeleton** (StateGraph with 3 nodes: dispatch, orchestrate, aggregate)
5. **Shared state schema** (FleetState, AgentMessage protocol)
6. **First commit:** "Infrastructure ready. All agents can start building."

---

## 16. The Pitch to Your Team

> "We're building 9-11 agents across 3 tiers. Tier 1 (5 agents) is infrastructure—we all own it together. Tier 2 (4 agents) is excellence—you pick your specialty (fairness, security, governance, or UI). Tier 3 (4 agents) is bonus if we have energy.
>
> Each person has 1 primary agent for the individual report. Clear ownership. Parallel execution. No bottlenecks.
>
> The difference between A and A+? We don't just detect fairness; we help drivers improve. We don't just log decisions; we explain them to stakeholders. We don't just follow frameworks; we map all 3 (IMDA + GenAI + FEAT).
>
> Let's build an A+."

---

**This is your master plan. Everything is decided. You're ready to execute.**
