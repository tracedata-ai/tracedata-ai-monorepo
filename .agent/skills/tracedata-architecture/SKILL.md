---
name: TraceData Architecture Enforcer
description: Enforces the architectural constraints for the TraceData capstone project (Agentic AI Middleware + Next.js).
---

# TraceData Architecture Enforcer

This skill must be referenced whenever discussing, planning, or writing code for the TraceData Capstone project.

## Core Architectural Constraints

1. **Architecture Pattern**: 
   - **Agentic AI Middleware Monolith**: Built in Python (FastAPI + LangGraph).
   - **Frontend**: Next.js application.
   - **Strict Scope Boundary**: There is no full-featured traditional fleet management backend in Java. The fleet data schemas in PostgreSQL are nominal and only exist to support AI workflows.

2. **Ingestion & Data Pipelines (Kafka/MQTT)**:
   - **Dual Data Sources**: The Ingestion layer (`Ingestion Quality Agent`) receives two distinct data types:
     1. **Structured Telematics**: High-frequency pings from an onboard device/simulator (GPS, speed, RPM).
     2. **Unstructured Driver Input**: Free-text reviews, feedback, comments, and formal appeals submitted via the driver app.
   - **Batching Strategy (Telematics)**: The on-vehicle Telematic Control Unit (TCU) collects pings at 10 to 30-second intervals. Under normal operation, these are collated and sent up in a single batch every 4 to 10 minutes (Normal Pipe).
   - **Critical Bypass**: High severity anomalies (accidents, extreme harsh braking) bypass the batching collator and are sent immediately via a distinct Critical Events pipe.
   - **Routing Rules**: The Deterministic Ingestion Router selectively hands over only unstructured user-generated content (text/appeals) to the AI-based **PII Scrubber Agent**. Pure structured telemetry is scrubbed deterministically and persisted without invoking an LLM.

3. **Context Enrichment (MCP)**:
   - **Input**: Raw GPS coordinates and timestamps.
   - **Output**: The Context Enrichment Agent leverages Model Context Protocol (MCP) to fetch rich geographic details (Place Name, Topology, Local Weather, Real-Time Traffic Conditions). 
   - **Usage**: It serves as a shared, high-speed Tool Service (returning in < 2 seconds) used by Behavior, Safety, and Orchestrator agents to build situational awareness.

4. **Driver Encouragement & Profiling**:
   - **Objective**: The system must go beyond penalization to build an encouragement profile. Raw telemetry points (the 10-30s intervals) must be aggregated and crunched to detect positive driving patterns (e.g., maintaining safe following distances, smooth deceleration). 
   - **Reasoning**: The AI (Orchestrator or Coaching Agent) will use these aggregated data points and contextual anomalies (e.g., "I swerved because of a deer") to reason autonomously, sometimes deciding to route commands to the Behavior Model to forgive penalties or boost encouragement scores.

5. **Safety Intervention (Multi-Level)**:
   - Evaluated by the Safety Agent working in near real-time on the Critical Events pipe:
   - **Level 1 (Minor)**: App notification / in-cab reminder.
   - **Level 2 (Moderate)**: Formal message logged and sent to driver.
   - **Level 3 (Serious)**: Direct escalation/call initiated to the driver via Fleet Manager.

6. **Internal State & Persistence**:
   - **PostgreSQL (`pgvector`)**: Mandatory. The database must use `pgvector` to enable the AI agents to perform semantic search against historical driver profiles, text submissions, and behavioral patterns.
   - **Table Segregation**: Each processing agent writes its outputs to distinct tables (schema separation based on agent), correlated strongly by a unique `trip_id`.
   - **Redis + Celery**: Used for handling asynchronous task queuing and internal background processing within the middleware.

7. **Telematics Data Shape (Flat Schema)**:
   - **Structure**: All incoming telemetry MUST be processed and stored using a flattened, sparse JSON schema (NO deeply nested object hierarchies). 
   - **Sparsity**: The schema is highly scalable; event-specific fields that are not relevant to the current `event_type` or lack valid data MUST be omitted entirely from the device payload (not sent) to save bandwidth.
   - **XAI Optimization**: All type-specific features must be contained within a single `details` dictionary. This ensures that downstream ML models (XGBoost) and Explainable AI tools (AIF360, SHAP/LIME) receive a uniform, easily comparable feature space.
   - **Ping Load Classification**: The system explicitly handles four ping types: `Emergency Ping` (critical bypass), `Normal Ping` (4-min batched), `Start of Trip Ping`, and `End of Trip Ping`.
   - **Incident Media**: For any harsh or critical event, the physical device securely uploads 15 seconds of pre/post-incident video/photos to an AWS S3 bucket. The generated S3 URL is then appended to the corresponding telemetry ping payload.

8. **AI Security & Guardrails**:
   - **LLM Rate Limiting & Quotas**: Implement strict per-driver token/call quotas to prevent LLM cost explosion.
   - **Prompt Sanitization**: All user-generated text MUST be sanitized and inserted into explicitly templated prompts to mitigate Prompt Injection.
   - **Fairness Circuit Breakers**: The system must actively monitor the Statistical Parity Difference (SPD). If fairness drift exceeds thresholds (>0.2), manual FM overrides and AIF360 retraining workflows must trigger.
   - **Degradation & Fallbacks**: Provide deterministic rule-based fallbacks for instances where the LLM API times out, halls, or telemetry data is degraded/missing.
   - **Data Privacy**: Enforce strict RBAC (JWT) and encryption (AES-256) for all driver-submitted feedback or appeals to prevent unauthorized visibility by Fleet Managers.

## Directives for AI Agents

- **Always verify constraints**: Before scaffolding new services, confirm they fit within the Python FastAPI + LangGraph boundary.
- **Do not introduce microservices**: Focus entirely on the Agentic middleware logic.
- **Traceability first**: Ensure all agent actions write to their respective Postgres tables with the `trip_id` identifier.
