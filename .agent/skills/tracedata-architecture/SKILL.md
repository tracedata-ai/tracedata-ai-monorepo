---
name: TraceData Architecture Enforcer
description: Enforces the architectural constraints for the TraceData capstone project (Agentic AI Middleware + Next.js).
---

# TraceData Architecture Enforcer

This skill must be referenced whenever discussing, planning, or writing code for the TraceData Capstone project.

## Core Architectural Constraints

1. **Architecture Pattern**: 
   - **Agentic AI Middleware Monolith**: Built in Python (FastAPI + LangGraph). 
   - **Frontend**: Next.js application built with **Tailwind CSS** and **Shadcn UI**.
   - **Multi-Tenancy**: Mandatory. All data layers (Telematics, Driver Profiles, Trip Logs) must include and enforce a `tenant_id` for strict data isolation.

2. **Ingestion & Data Pipelines (Kafka/MQTT)**:
   - **Dual Data Sources**: The Ingestion layer (`Ingestion Quality Agent`) receives two distinct data types:
     1. **Structured Telematics**: High-frequency pings from an onboard device/simulator (GPS, speed, RPM).
     2. **Unstructured Driver Input**: Free-text reviews, feedback, comments, and formal appeals submitted via the driver app.
   - **Batching Strategy (Telematics)**: The on-vehicle Telematic Control Unit (TCU) collects pings at 10 to 30-second intervals. Under normal operation, these are collated and sent up in a single batch every 4 to 10 minutes (Normal Pipe).
   - **Critical Bypass**: High severity anomalies (accidents, extreme harsh braking) bypass the batching collator and are sent immediately via a distinct Critical Events pipe.
   - **Tenant Routing**: Every payload must explicitly contain a `tenant_id` to ensure proper routing and persistence.

3. **Frontend & UI Standards**:
   - **Framework**: Next.js (App Router).
   - **Styling**: Tailwind CSS for layout and utilities.
   - **Components**: Shadcn UI for all interactive elements (Buttons, Tables, Sheets, Dialogs).
   - **Patterns**: Use the "Headless Table + Slots" pattern for data-heavy views (Drivers, Trips, Fleet) to maintain consistency and reusability.

4. **Context Enrichment (MCP)**:
   - **Input**: Raw GPS coordinates and timestamps.
   - **Output**: The Context Enrichment Agent leverages Model Context Protocol (MCP) to fetch rich geographic details (Place Name, Topology, Local Weather, Real-Time Traffic Conditions). 
   - **Usage**: It serves as a shared, high-speed Tool Service (returning in < 2 seconds) used by Behavior, Safety, and Orchestrator agents to build situational awareness.

5. **Driver Encouragement & Profiling**:
   - **Objective**: The system must go beyond penalization to build an encouragement profile. Raw telemetry points (the 10-30s intervals) must be aggregated and crunched to detect positive driving patterns.
   - **Reasoning**: The AI (Orchestrator or Coaching Agent) will use these aggregated data points and contextual anomalies to reason autonomously, deciding when to boost encouragement scores.

6. **Safety Intervention (Multi-Level)**:
   - Evaluated by the Safety Agent working in near real-time on the Critical Events pipe:
   - **Level 1 (Minor)**: App notification / in-cab reminder.
   - **Level 2 (Moderate)**: Formal message logged and sent to driver.
   - **Level 3 (Serious)**: Direct escalation/call initiated to the driver via Fleet Manager.

7. **Internal State & Persistence**:
   - **PostgreSQL (`pgvector`)**: Mandatory for semantic search against historical profiles and text submissions.
   - **Table Segregation**: Each processing agent writes its outputs to distinct tables, correlated by `trip_id` and isolated by `tenant_id`.
   - **Redis + Celery**: Used for asynchronous task queuing and internal background processing.

8. **Telematics Data Shape (Flat Schema)**:
   - **Structure**: Flattened, sparse JSON schema. Omit irrelevant fields to save bandwidth.
   - **XAI Optimization**: Use a uniform `details` dictionary for downstream ML and Explainable AI tools.
   - **Ping Load Classification**: `Emergency Ping`, `Normal Ping`, `Start of Trip Ping`, and `End of Trip Ping`.
   - **Incident Media**: AWS S3 URLs appended to telemetry for critical events.

9. **AI Security & Guardrails**:
   - **LLM Rate Limiting**: Strict per-driver/per-tenant token quotas.
   - **Prompt Sanitization**: Explicit templating to mitigate Prompt Injection.
   - **Fairness**: Monitor Statistical Parity Difference (SPD); trigger retraining if drift > 0.2.
   - **Data Privacy**: RBAC (JWT) and encryption (AES-256) for driver feedback.

## Directives for AI Agents

- **Always verify constraints**: Before scaffolding new services, confirm they fit within the Python FastAPI + LangGraph + Next.js boundary.
- **Tenant Context**: Never process or store data without a validated `tenant_id`.
- **Traceability first**: Ensure all agent actions write to their respective Postgres tables with the `trip_id` identifier.
