# TraceData System Architecture

Designed to support execution of the [Master Plan v2.1](master_plan.md): 7 agents across 3 tiers, ~45 person-days effort, 4-week timeline.

## Overview

TraceData is a multi-agent AI intelligence middleware system designed to attach to existing truck fleet management infrastructure. This document provides a comprehensive overview of the system architecture, technology stack, and design patterns.

## Table of Contents

1. [Architecture Layers](#architecture-layers)
2. [Technology Stack](#technology-stack)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Agent Tier Structure](#agent-tier-structure)
6. [Deployment Architecture](#deployment-architecture)
7. [Security & Observability](#security--observability)
8. [Performance Considerations](#performance-considerations)

## Architecture Layers

TraceData follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                    │
│  (Web Dashboard, RAG Chat, Geo-Spatial Heatmaps, APIs)      │
├─────────────────────────────────────────────────────────────┤
│                   REASONING LAYER                           │
│  (Driver Behaviour, Compliance, Recourse, Orchestrator)     │
├─────────────────────────────────────────────────────────────┤
│                 PROCESSING LAYER                            │
│     (Ingestion, PII Cleaner, State Management)              │
├─────────────────────────────────────────────────────────────┤
│              PLATFORM INFRASTRUCTURE LAYER                  │
│     (Observability, Audit Logs, Cost Tracking, Health)      │
├─────────────────────────────────────────────────────────────┤
│                      DATA LAYER                             │
│        (Kafka, PostgreSQL, pgvector, Cache)                 │
└─────────────────────────────────────────────────────────────┘
```

### 1. Data Layer

**Purpose:** Persistent and streaming data storage

| Component        | Technology       | Purpose                                   |
| ---------------- | ---------------- | ----------------------------------------- |
| **Event Stream** | Apache Kafka     | Real-time telemetry from fleet devices    |
| **Analytics DB** | PostgreSQL       | Structured data: trips, scores, decisions |
| **Vector Store** | pgvector         | Embeddings for RAG semantic search        |
| **Cache**        | Redis (optional) | Session state, model cache                |

**Key Design Decisions:**

- Kafka for high-throughput, low-latency telemetry (IoT-style data)
- PostgreSQL for ACID compliance and audit trail immutability
- pgvector for semantic search in RAG without external dependencies

### 2. Processing Layer

**Purpose:** Ingest, validate, and prepare data for reasoning agents

| Component            | Technology              | Purpose                                          |
| -------------------- | ----------------------- | ------------------------------------------------ |
| **Ingestion Engine** | Python + Kafka Consumer | Subscribe to telemetry, batch into trip segments |
| **PII Cleaner**      | Python + Regex          | Deterministic masking before ML pipeline         |
| **State Manager**    | LangGraph               | Manage FleetState across agents                  |

**Data Flow:**

```
Kafka Stream → Validation → PII Masking → Trip Batching → FleetState
```

### 3. Reasoning Layer

**Purpose:** Multi-agent AI reasoning with coordinated inference

| Component                  | Technology              | Purpose                              |
| -------------------------- | ----------------------- | ------------------------------------ |
| **Orchestrator**           | LangGraph StateGraph    | Route requests to specialized agents |
| **Driver Behaviour Agent** | XGBoost + AIF360 + SHAP | Risk scoring + fairness correction   |
| **Compliance Agent**       | LLM + Rule Engine       | Regulatory reasoning + edge cases    |
| **Recourse Agent (PoC)**   | Python Counterfactuals  | "What-if" explanations               |

**LLM Choice:** OpenAI GPT-4o-mini

- Cost-optimized (lower token pricing)
- Fast inference (critical for real-time flows)
- Strong reasoning capability for hybrid logic

### 4. Platform Infrastructure Layer

**Purpose:** Observability, auditing, and system health

| Service           | Technology        | Purpose                                |
| ----------------- | ----------------- | -------------------------------------- |
| **Tracing**       | LangSmith         | LLM call instrumentation + debugging   |
| **Audit Logging** | PostgreSQL        | Immutable decision logs for compliance |
| **Cost Tracking** | Custom Middleware | Token usage + latency per agent        |
| **Health Checks** | Prometheus        | Alert if agents unhealthy or degraded  |

**Why Not A Separate Agent?**
These are platform-level concerns, not domain-specific reasoning. Implemented as cross-cutting middleware to avoid bloating agent count.

### 5. User Interface Layer

**Purpose:** Surface insights to fleet managers and operators

| Component               | Technology  | Purpose                                     |
| ----------------------- | ----------- | ------------------------------------------- |
| **Web Dashboard**       | Next.js     | XAI visualizations (SHAP, LIME waterfall)   |
| **RAG Chatbot**         | React       | "Why did Driver X get score Y?" Q&A         |
| **Geo-Spatial Heatmap** | Mapbox + D3 | Harsh-braking hotspots (privacy-preserving) |
| **REST API**            | FastAPI     | Third-party integrations                    |

## Technology Stack

### Backend

| Layer                  | Tool             | Justification                               |
| ---------------------- | ---------------- | ------------------------------------------- |
| **Framework**          | FastAPI (Python) | Async-first, auto-docs, minimal boilerplate |
| **Agent Coordination** | LangGraph        | StateGraph for deterministic routing        |
| **LLM Abstraction**    | LangChain        | Model-agnostic interface                    |
| **ML Model**           | XGBoost          | Interpretable, SHAP support, fast training  |
| **Fairness**           | AIF360           | Industry-standard bias detection/correction |
| **Explainability**     | SHAP + LIME      | Course-aligned, production-proven           |
| **Security Testing**   | Promptfoo        | 100+ adversarial tests for LLM injection    |
| **Code Security**      | Bandit           | Static analysis for Python vulnerabilities  |

### Database & Storage

| Tool                 | Purpose                                     | Rationale                                              |
| -------------------- | ------------------------------------------- | ------------------------------------------------------ |
| **PostgreSQL**       | Structured data (trips, scores, audit logs) | ACID compliance, JSON support, window functions        |
| **pgvector**         | Semantic search for RAG                     | Eliminates external vector DB dependency               |
| **Kafka**            | Event streaming (fleet telemetry)           | High throughput, partitioned topics, replay capability |
| **Redis (Optional)** | Session cache + model weights               | Fast in-memory access for real-time scoring            |

### Frontend

| Tool          | Purpose                                                  |
| ------------- | -------------------------------------------------------- |
| **Next.js**   | Server-side rendering, API routes, deployment simplicity |
| **React**     | Interactive dashboards, real-time updates                |
| **Plotly/D3** | SHAP waterfall, LIME local explanations                  |
| **Mapbox**    | Geographic heatmap rendering                             |

### DevOps & Deployment

| Tool                   | Purpose                            |
| ---------------------- | ---------------------------------- |
| **Docker**             | Containerized agents + services    |
| **AWS ECS Fargate**    | Serverless container orchestration |
| **GitHub Actions**     | CI/CD: lint → test → deploy        |
| **Terraform (Future)** | Infrastructure as Code             |

## Agent Tier Structure

TraceData is built on **7 agents across 3 tiers**, strictly aligned with execution credibility and realistic scope.

### Tier 1: MUST (Core Backbone — 4 Agents)

**Status:** Fully committed implementation  
**Effort:** ~15-20 person-days (~4-5 days per person)  
**Success Criteria:** Pipeline operational, fairness detected, system stable

| Agent                | Technology              | Module Alignment                         | Risk   | Purpose                                                           |
| -------------------- | ----------------------- | ---------------------------------------- | ------ | ----------------------------------------------------------------- |
| **Ingestion Engine** | Kafka Consumer (Python) | Module 4: MLSecOps                       | 6.0/10 | Subscribe to live fleet telemetry, batch into trip segments       |
| **PII Cleaner**      | Python Regex + Jitter   | Module 2: Cybersecurity                  | 3.0/10 | Deterministic masking (zero-LLM), spatial jittering               |
| **Driver Behaviour** | XGBoost + AIF360 + SHAP | Module 1: XRAI/Fairness                  | 6.5/10 | Risk scoring, bias detection & correction, feature importance     |
| **Orchestrator**     | LangGraph StateGraph    | Module 3: Agentic AI, Module 4: MLSecOps | 7.5/10 | Multi-agent coordination, deterministic routing, state management |

**Platform Observability (Infrastructure, Not An Agent)**

- LangSmith: LLM call instrumentation
- Audit Logging: Immutable decision logs (PostgreSQL)
- Cost Tracking: Token usage + latency per agent
- Health Checks: System alerts on degradation

### Tier 2: GOOD (Governance & Excellence — 2 Full + 2 PoCs)

**Status:** Full implementations + conceptual proofs  
**Effort:** ~20-26 person-days (~5-7 days per person additional)

#### 2a. Full Implementations (16-20 days)

| Agent                   | Technology                    | Module Alignment                                             | Risk   | Purpose                                                            |
| ----------------------- | ----------------------------- | ------------------------------------------------------------ | ------ | ------------------------------------------------------------------ |
| **Compliance & Safety** | Rule Engine + LLM + STRIDE    | Module 2: Cybersecurity, Module 3: Hybrid Reasoning          | 6.5/10 | HOS rules, LLM edge-case reasoning, threat modeling                |
| **RAG Assistant**       | LangChain + pgvector + OpenAI | Module 2: Prompt Security, Module 4: Stakeholder Interaction | 5.5/10 | Fleet manager Q&A, 3-layer security (regex → LLM → Moderation API) |

#### 2b. Proof-of-Concept Implementations (4-6 days)

| Agent (PoC)             | Technology                         | Module Alignment            | Risk   | Purpose                                                                               |
| ----------------------- | ---------------------------------- | --------------------------- | ------ | ------------------------------------------------------------------------------------- |
| **Actionable Recourse** | Python Counterfactuals             | Module 1: Fairness Recourse | 4.0/10 | Simple counterfactual: "If harsh_braking -2, score crosses threshold" (NOT full DiCE) |
| **Appeals Adjudicator** | Workflow Documentation + UI Mockup | Module 1: HITL Governance   | 3.0/10 | Document HITL workflow, basic mockup for decision review                              |

### Tier 3: NICE (Stretch Goal — 1 Agent)

**Status:** Optional, if time/energy permits  
**Effort:** ~3-4 person-days (deferred)

| Agent                        | Technology                   | Module Alignment      | Purpose                                                              |
| ---------------------------- | ---------------------------- | --------------------- | -------------------------------------------------------------------- |
| **Geo-Spatial Intelligence** | Mapbox + D3 + Privacy Jitter | Module 1: Spatial XAI | Heatmaps of harsh-braking hotspots, privacy-preserving visualization |

## System Components

### Component Interaction Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        FLEET["Fleet Devices<br/>(GPS, OBD, Telematics)"]
    end

    subgraph "Data Ingestion"
        KAFKA["Kafka Cluster<br/>Event Stream"]
        ING["Ingestion Engine<br/>(Consumer, Windowing)"]
    end

    subgraph "Data Processing"
        PII["PII Cleaner<br/>(Masking, Jitter)"]
        STATE["State Manager<br/>(FleetState)"]
    end

    subgraph "Reasoning (Tier 1 MUST)"
        ORCH["🎯 Orchestrator<br/>(LangGraph StateGraph)"]
        BEHAVIOR["⚖️ Driver Behaviour<br/>(XGBoost + AIF360 + SHAP)"]
    end

    subgraph "Governance (Tier 2 GOOD)"
        COMPLIANCE["📋 Compliance & Safety<br/>(Rules + LLM)<br/>FULL"]
        CHAT["🤖 RAG Assistant<br/>(LangChain + pgvector)<br/>FULL"]
        RECOURSE["💡 Actionable Recourse<br/>(Counterfactuals)<br/>PoC"]
        APPEALS["✅ Appeals Adjudicator<br/>(Workflow + Mockup)<br/>PoC"]
    end

    subgraph "Visualization (Tier 3 STRETCH)"
        MAP["🗺️ Geo-Spatial Intel<br/>(Mapbox + D3)"]
    end

    subgraph "Platform Services"
        AUDIT["Audit Log<br/>(PostgreSQL)"]
        TRACE["LangSmith<br/>(Tracing)"]
        COST["Cost Tracking<br/>(Middleware)"]
    end

    subgraph "Storage"
        DB["PostgreSQL<br/>(Decisions, Trips)"]
        VEC["pgvector<br/>(Embeddings)"]
        CACHE["Redis<br/>(Optional)"]
    end

    subgraph "User Interface"
        API["REST API<br/>(FastAPI)"]
        DASH["Dashboard<br/>(Next.js)"]
        CHAT["RAG Chatbot<br/>(React)"]
        MAP["Heatmap<br/>(Mapbox)"]
    end

    FLEET --> KAFKA
    KAFKA --> ING
    ING --> PII
    PII --> STATE
    STATE --> ORCH
    ORCH --> BEHAVIOR
    ORCH --> COMPLIANCE
    BEHAVIOR --> RECOURSE
    BEHAVIOR --> AUDIT
    COMPLIANCE --> AUDIT
    RECOURSE --> AUDIT
    ORCH --> TRACE
    ORCH --> COST
    AUDIT --> DB
    BEHAVIOR --> DASH
    CHAT --> VEC
    ORCH --> API
    API --> DASH
    API --> CHAT
    API --> MAP

    style FLEET fill:#e3f2fd
    style KAFKA fill:#ffebee
    style ING fill:#ffebee
    style PII fill:#ffebee
    style STATE fill:#ffebee
    style ORCH fill:#ef5350,color:#fff
    style BEHAVIOR fill:#ef5350,color:#fff

    style COMPLIANCE fill:#fdd835,color:#000
    style CHAT fill:#fdd835,color:#000
    style RECOURSE fill:#ffccbc,color:#000
    style APPEALS fill:#ffccbc,color:#000

    style MAP fill:#81c784,color:#000
    style AUDIT fill:#f3e5f5
    style TRACE fill:#f3e5f5
    style COST fill:#f3e5f5
    style DB fill:#e8f5e9
    style VEC fill:#e8f5e9
    style CACHE fill:#e8f5e9
    style API fill:#fce4ec
    style DASH fill:#fce4ec
    style CHAT fill:#fce4ec
    style MAP fill:#fce4ec
```

### Tier Execution Strategy

**Week 1 Critical Path:** Ingestion → PII → Orchestrator (12 days)  
**Week 2-3 Block:** Driver Behaviour + Compliance + RAG (22-25 days)  
**Week 3 Stretch:** PoCs + Geo-Spatial if time permits (7-8 days)  
**Week 4 Validation:** Testing + individual reports (8 days)

---

## Data Flow

### Critical Path: Trip Scoring

```
1. Telemetry Event (from device)
   └─ GPS, RPM, braking force, HOS time, etc.

2. Ingest & Batch (Ingestion Engine)
   └─ Kafka consumer aggregates into trip_segment

3. PII Masking (PII Cleaner)
   └─ Regex: strip driver name/ID
   └─ Jitter: reduce GPS precision to ±100m

4. Orchestrator Routes
   └─ Receives cleaned trip_data
   └─ Dispatches to Driver Behaviour Agent

5. Driver Behaviour Scores
   └─ XGBoost model: harsh_braking, speed_variance, hos_compliance
   └─ AIF360 fairness check: detect demographic bias
   └─ SHAP explains why score = 0.68

6. Store Results
   └─ PostgreSQL: trip record + score + audit log
   └─ Kafka: publish risk_event for downstream consumers

7. RAG Chatbot Answers
   └─ Semantic search in pgvector: find similar trips
   └─ LLM generates: "Driver scored low due to speed variance"
```

### Module Alignment (SWE5008 Rubric)

| Module                     | Implementation Evidence                                                 | Agents                                          |
| -------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------- |
| **Mod 1: XRAI & Fairness** | AIF360 bias detection + SHAP explanations + counterfactual recourse PoC | Driver Behaviour, Actionable Recourse, Appeals  |
| **Mod 2: Cybersecurity**   | PII masking (PDPA) + STRIDE threat modeling + prompt injection defense  | PII Cleaner, Compliance & Safety, RAG Assistant |
| **Mod 3: Agentic AI**      | LangGraph coordination + hybrid rules+LLM reasoning                     | Orchestrator, Compliance & Safety               |
| **Mod 4: MLSecOps**        | Kafka streaming + LangSmith tracing + audit logging + cost tracking     | Ingestion Engine, Platform Observability        |

| Operation             | Latency Budget | Reason                         |
| --------------------- | -------------- | ------------------------------ |
| **Ingestion → Score** | < 2 sec        | Near real-time for dashboards  |
| **PII Masking**       | < 100 ms       | High throughput, deterministic |
| **XGBoost Inference** | < 500 ms       | Batched predictions            |
| **SHAP Explanation**  | < 1 sec        | Background job acceptable      |
| **Compliance Rules**  | < 200 ms       | Blocking decision path         |

## Agent Tier Structure

### Tier 1: Core Backbone (MUST)

- **Ingestion Engine** → data pipeline foundation
- **PII Cleaner** → security checkpoint
- **Driver Behaviour** → core ML reasoning
- **Orchestrator** → multi-agent coordinator

**Effort:** ~15-20 person-days  
**Blockers:** None (independent implementation)

### Tier 2: Governance & Excellence (GOOD)

- **Compliance & Safety** (Full) → regulatory reasoning
- **RAG Assistant** (Full) → stakeholder communication
- **Actionable Recourse** (PoC) → fairness recourse demo
- **Appeals Adjudicator** (PoC) → HITL workflow

**Effort:** ~20-26 person-days  
**Blockers:** Depends on Tier 1 outputs

### Tier 3: Stretch Goal (NICE)

- **Geo-Spatial Intelligence** → heatmap visualization

**Effort:** ~3-4 person-days if time permits

## Deployment Architecture

### Quick Comparison: Cloud Platform Options

| Aspect             | DigitalOcean (Preferred) | AWS              | Azure               | GCS            |
| ------------------ | ------------------------ | ---------------- | ------------------- | -------------- |
| **Compute**        | App Platform             | ECS Fargate      | Container Instances | Cloud Run      |
| **Database**       | Managed PostgreSQL       | RDS PostgreSQL   | Azure Database      | Cloud SQL      |
| **Messaging**      | Droplet + Kafka          | MSK              | Event Hubs          | Pub/Sub        |
| **Caching**        | Managed Redis            | ElastiCache      | Azure Cache         | Memorystore    |
| **Cost**           | $40-60/mo                | $60-120/mo       | $50-100/mo          | $20-60/mo      |
| **Learning Curve** | Very Low                 | Medium           | Medium              | Low            |
| **Best For**       | MVP Launch               | Enterprise Scale | Compliance-Heavy    | Cost-Conscious |

### Option 1: DigitalOcean (🌟 Recommended for MVP)

**Why DigitalOcean?** Simplest architecture, transparent pricing, perfect for 4-person startup team, minimal DevOps overhead.

```mermaid
graph TB
    subgraph DO["DigitalOcean Account"]
        subgraph APP["App Platform"]
            WEB["Web Service: Next.js<br/>2-3 instances<br/>$12-30/mo"]
            API["Web Service: FastAPI<br/>2-4 instances<br/>$12-30/mo"]
            WORKER["Worker: Scheduler<br/>Background jobs<br/>$6-12/mo"]
        end

        subgraph MANAGED["Managed Services"]
            PG["Managed PostgreSQL<br/>Single/High-Availability<br/>$15-25/mo"]
            REDIS["Managed Redis<br/>Session cache<br/>$7-15/mo"]
            KAFKA["Droplet + Strimzi<br/>Kafka broker<br/>$12-18/mo"]
        end
    end

    APP --> MANAGED
    WEB -.->|HTTP| API
    API --> KAFKA
    API --> REDIS
    API --> PG
    WORKER --> PG

    style DO fill:#0080ff,color:#fff
    style APP fill:#0099cc,color:#fff
    style WEB fill:#00ccff,color:#000
    style API fill:#00ccff,color:#000
    style WORKER fill:#00ccff,color:#000
    style MANAGED fill:#004d80,color:#fff
    style PG fill:#1fa67a,color:#fff
    style REDIS fill:#1fa67a,color:#fff
    style KAFKA fill:#666,color:#fff
```

**Setup (5 minutes):**

```bash
# 1. Create PostgreSQL database via Dashboard
doctl databases create tracedata -e postgres

# 2. Create Redis cache
doctl databases create cache -e redis

# 3. Deploy via GitHub integration (push code → auto-deploy)
doctl apps create
# Provides: app.yaml for git-based deployments

# 4. Point domain to App Platform load balancer
# Cost: $0/domain + $40-60/mo for services
```

**Estimated Monthly Cost:** $40-60/mo all-inclusive

---

### Option 2: AWS (ECS Fargate - Enterprise Scale)

**Why AWS?** Multi-AZ reliability, advanced monitoring, auto-scaling at massive scale, 100K+ concurrent users.

```mermaid
graph TB
    subgraph AWS["AWS Region"]
        subgraph VPC["VPC Private Network"]
            subgraph PUBLIC["Public Subnet"]
                ALB["ALB Load Balancer<br/>Routes HTTP/HTTPS"]
            end

            subgraph PRIVATE["Private Subnet AZ-1,2"]
                API1["ECS Fargate<br/>FastAPI<br/>2+ replicas"]
                WEB1["ECS Fargate<br/>Next.js<br/>2+ replicas"]
            end

            subgraph DB_SUBNET["Database Subnet"]
                RDS["RDS PostgreSQL<br/>Multi-AZ + Read Replicas<br/>Auto-backup"]
                CACHE["ElastiCache Redis<br/>Multi-AZ<br/>Session cache"]
            end

            subgraph KAFKA_SUBNET["Streaming Layer"]
                MSK["MSK Kafka Cluster<br/>3 brokers Multi-AZ<br/>Auto-scaling"]
            end
        end

        subgraph MONITORING["Observability"]
            CW["CloudWatch<br/>Logs, Metrics, Alarms"]
            XRay["X-Ray<br/>Distributed tracing"]
        end
    end

    ALB --> API1
    ALB --> WEB1
    MSK --> API1
    API1 --> RDS
    API1 --> CACHE
    API1 --> CW
    WEB1 --> RDS
    WEB1 --> CW
    RDS --> CW

    style AWS fill:#ff9900,color:#000
    style ALB fill:#e3f2fd,color:#000
    style API1,WEB1 fill:#ffebee,color:#000
    style RDS,CACHE fill:#c8e6c9,color:#000
    style MSK fill:#ffe0b2,color:#000
    style CW,XRay fill:#b0bec5,color:#000
```

**Setup (CloudFormation):**

```bash
# 1. Create VPC, subnets, security groups (via CloudFormation)
aws cloudformation create-stack --stack-name tracedata-vpc \
  --template-body file://vpc-template.yaml

# 2. Deploy RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier tracedata-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin

# 3. Push Docker images to ECR
aws ecr create-repository --repository-name tracedata-api
docker build -t api backend/
docker tag api:latest ACCOUNT.dkr.ecr.REGION.amazonaws.com/tracedata-api:latest
aws ecr get-login-password | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.REGION.amazonaws.com
docker push ACCOUNT.dkr.ecr.REGION.amazonaws.com/tracedata-api:latest

# 4. Create ECS task definitions and services
aws ecs register-task-definition --cli-input-json file://task-def.json
aws ecs create-service --cluster tracedata --service-name api --task-definition tracedata-api:1

# Cost: $60-120/mo for development; $200+/mo for production multi-AZ
```

**Estimated Monthly Cost:** $60-120/mo (development) → $200+/mo (production)

---

### Option 3: Azure (Container Instances + App Service)

**Why Azure?** Enterprise compliance, Active Directory integration, on-premises hybrid options, cost optimizations via reserved instances.

```mermaid
graph TB
    subgraph AZURE["Azure Subscription"]
        subgraph CONTAINERS["Container Workloads"]
            API["Container Instances<br/>FastAPI<br/>1-2 instances<br/>$15-30/mo"]
            WEB["App Service<br/>Next.js<br/>Auto-scale<br/>$10-25/mo"]
            JOB["Container Instances<br/>Scheduler<br/>On-demand<br/>$3-8/mo"]
        end

        subgraph STORAGE["Data Services"]
            DB["Azure Database<br/>PostgreSQL Flexible<br/>Burstable B1s tier<br/>$12-30/mo"]
            CACHE["Azure Cache<br/>for Redis<br/>Basic C0<br/>$18/mo"]
            EVENTS["Event Hubs<br/>Standard tier<br/>Kafka alternative<br/>$100/month"]
        end

        subgraph MONITORING["Observability"]
            INSIGHTS["Application Insights<br/>Logs & metrics"]
            MONITOR["Azure Monitor<br/>Alerts & dashboards"]
        end
    end

    CONTAINERS --> STORAGE
    API --> CACHE
    API --> EVENTS
    WEB --> DB
    JOB --> DB
    CONTAINERS --> MONITORING

    style AZURE fill:#0078d4,color:#fff
    style CONTAINERS fill:#50e6ff,color:#000
    style API,WEB,JOB fill:#107c10,color:#fff
    style STORAGE fill:#00bcf2,color:#000
    style DB,CACHE fill:#7fba00,color:#fff
    style EVENTS fill:#ffc900,color:#000
    style MONITORING fill:#4a4a4a,color:#fff
```

**Setup (Azure CLI):**

```bash
# 1. Create resource group
az group create --name tracedata-rg --location eastus

# 2. Deploy PostgreSQL
az postgres flexible-server create \
  --resource-group tracedata-rg \
  --name tracedata-db \
  --sku-name Standard_B1s \
  --storage-size 32

# 3. Deploy container instances
az container create \
  --resource-group tracedata-rg \
  --name tracedata-api \
  --image YOUR_REGISTRY.azurecr.io/tracedata-api:latest \
  --cpu 1 --memory 1

# 4. Deploy via App Service
az appservice plan create --name tracedata-plan \
  --resource-group tracedata-rg --sku B1 --is-linux

az webapp create --resource-group tracedata-rg \
  --plan tracedata-plan --name tracedata-web \
  --deployment-container-image-name YOUR_IMAGE

# Cost: $50-100/mo
```

**Estimated Monthly Cost:** $50-100/mo

---

### Option 4: Google Cloud Run (Serverless - Best for Startups)

**Why GCS?** Generous free tier ($300/month), pay-per-request billing, ultra-fast deployment, excellent data analytics.

```mermaid
graph TB
    subgraph GCP["Google Cloud Project"]
        subgraph COMPUTE["Serverless Compute"]
            API["Cloud Run<br/>FastAPI<br/>0-100 instances<br/>$0.00002/request"]
            WEB["Cloud Run<br/>Next.js<br/>0-50 instances<br/>$0.00001/request"]
        end

        subgraph BATCH["Background Jobs"]
            SCHED["Cloud Scheduler<br/>Trigger Pub/Sub<br/>$0.10/job/month"]
            PUBSUB["Pub/Sub<br/>Event streaming<br/>$0.05/GB"]
        end

        subgraph DATA["Data Services"]
            DB["Cloud SQL<br/>PostgreSQL<br/>Shared tier: $8/mo<br/>or Serverless: $1/mo"]
            CACHE["Memorystore<br/>Redis<br/>$0.006/GB/hour<br/>mins: ~$50/mo"]
        end

        subgraph OBSERVABILITY["Observability"]
            LOGGING["Cloud Logging<br/>Free: 50GB/month"]
            TRACE["Cloud Trace<br/>Distributed tracing"]
        end
    end

    COMPUTE --> DATA
    BATCH --> CACHE
    API --> DB
    API --> CACHE
    API --> PUBSUB
    WEB --> DB
    COMPUTE --> OBSERVABILITY

    style GCP fill:#4285f4,color:#fff
    style COMPUTE fill:#5f9ea0,color:#fff
    style API,WEB fill:#00bcd4,color:#000
    style BATCH fill:#ff6f00,color:#fff
    style SCHED,PUBSUB fill:#fb8500,color:#fff
    style DATA fill:#34a853,color:#fff
    style DB,CACHE fill:#fbbc04,color:#000
    style OBSERVABILITY fill:#9c27b0,color:#fff
```

**Setup (gcloud CLI - 3 minutes):**

```bash
# 1. Deploy FastAPI to Cloud Run
gcloud run deploy tracedata-api \
  --source ./backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=$DB_URL

# 2. Deploy Next.js frontend
gcloud run deploy tracedata-web \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# 3. Create Cloud SQL PostgreSQL
gcloud sql instances create tracedata-db \
  --database-version POSTGRES_15 \
  --tier db-f1-micro \
  --region us-central1

# 4. Create Memorystore Redis
gcloud redis instances create tracedata-redis \
  --size 1 \
  --region us-central1

# Free tier covers: $300/month = entire setup for months 1-3!
# After free credits: ~$20-60/mo
```

**Estimated Monthly Cost:** $20-60/mo (after free tier, much cheaper with Serverless SQL)

---

### Local Development (Identical Across All Platforms)

```bash
# Same environment works for DigitalOcean, AWS, Azure, GCS deploys
docker-compose up

# Services:
# - PostgreSQL (localhost:5432)
# - Redis (localhost:6379)
# - Kafka (localhost:9092)
# - FastAPI (localhost:8000)
# - Next.js (localhost:3000)
# - Minio S3 (localhost:9000)
```

### Migration Path

**Recommended progression:**

1. **Weeks 1-2:** Start with DigitalOcean App Platform ($40/mo, instant deployment)
2. **Week 3:** Add AWS redundancy if scaling needed (multi-region)
3. **Week 4+:** Migrate to preferred long-term platform based on usage patterns

| Stage                     | Platform             | Rationale                |
| ------------------------- | -------------------- | ------------------------ |
| **MVP (0-100 users)**     | DigitalOcean         | Fastest Time-to-Market   |
| **Growth (100-1K users)** | AWS ECS Fargate      | Auto-scaling reliability |
| **Scale (1K+ users)**     | AWS ECS + CloudFront | Multi-region global      |
| **Enterprise**            | Azure                | Compliance + governance  |

## Security & Observability

### Security Layers

1. **Data Privacy (PII Cleaner)**
   - Regex masking: driver names, IDs
   - Spatial jittering: GPS ±100m
   - Deterministic (zero-LLM): reproducible masking

2. **Prompt Security (RAG)**
   - Layer 1: Input regex (block known injection patterns)
   - Layer 2: LLM guardrails (system prompt constraints)
   - Layer 3: Moderation API (OpenAI Moderation)

3. **Access Control**
   - API key authentication (for third-party integrations)
   - JWT for web dashboard (future: OAuth2)
   - Database-level row-level security (future)

### Observability Stack

| Concern           | Tool              | Implementation                                 |
| ----------------- | ----------------- | ---------------------------------------------- |
| **LLM Tracing**   | LangSmith         | Every LLM call logged with inputs/outputs/cost |
| **Audit Trail**   | PostgreSQL        | Immutable append-only decision log             |
| **Cost Tracking** | Custom Middleware | Token usage, latency P95 per agent             |
| **Logs**          | CloudWatch        | Structured JSON logs from all services         |
| **Metrics**       | Prometheus        | Agent latency, cache hit rates, error rates    |
| **Alerts**        | SNS/Email         | Trips > 10min latency, fairness metrics drift  |

### Monitoring Dashboard (Future)

- Fairness metrics (demographic parity, equalized odds) trend over time
- Model performance (AUC, recall, precision) for drift detection
- Cost breakdown: tokens/dollar per agent per month
- Error rate: deployment rollback triggers on >5% failure rate

## Performance Considerations

### Scalability

| Component     | Throughput                      | Scaling Strategy                                |
| ------------- | ------------------------------- | ----------------------------------------------- |
| **Kafka**     | 100K+ msgs/sec                  | Multiple partitions = parallel consumers        |
| **Ingestion** | ~500 trips/sec (batched)        | Horizontal: run multiple consumer replicas      |
| **XGBoost**   | ~10K inferences/sec (batch 100) | GPU acceleration (optional), model quantization |
| **LLM API**   | Rate limited by OpenAI          | Request queuing + exponential backoff           |
| **DB**        | RDS t3.medium ~ 500 TPS         | Upgrade to t3.large if CPU > 80%                |

### Optimization Techniques

1. **Model Caching**
   - XGBoost model loaded once at startup
   - SHAP explanations cached for 1 hour

2. **Batch Processing**
   - Kafka consumer batches 100 trips every 30 sec
   - SHAP batch mode (simultaneous feature importance)

3. **Async Processing**
   - RAG embeddings computed async after trip stored
   - Compliance checks don't block main scoring pipeline

4. **Connection Pooling**
   - FastAPI: SQLAlchemy connection pool (min=5, max=20)
   - Kafka producer: batch.size=1024 bytes

### Resource Allocation (ECS Fargate)

| Service           | CPU (vCPU) | Memory (GB) | Replicas           |
| ----------------- | ---------- | ----------- | ------------------ |
| FastAPI + Agents  | 2          | 4           | 2 (autoscale to 4) |
| Next.js Frontend  | 1          | 2           | 2 (autoscale to 3) |
| Scheduler (batch) | 0.5        | 1           | 1                  |

## Future Architecture Improvements

1. **Model Training Pipeline**
   - Weekly retraining of XGBoost with new labels
   - A/B testing framework for model versions

2. **Distributed Tracing**
   - OpenTelemetry + Jaeger for cross-service spans

3. **Feature Store**
   - Tecton or Feast for feature versioning & serving

4. **Canary Deployments**
   - Route 5% traffic to new agent version, monitor metrics

5. **Kubernetes Migration**
   - ECS → EKS for multi-region deployment

---

**Document Version:** 1.0  
**Last Updated:** March 2026  
**Maintained By:** TraceData Architecture Team
