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
   - **NO Full-Scale Java Monolith**: Do not attempt to design or build a full-featured traditional fleet management backend in Java. The fleet data schemas in PostgreSQL are nominal and only exist to support AI workflows.

2. **Ingestion & Data Pipelines**:
   - **Apache Kafka**: Used for all external telemetry ingestion from truck devices to ensure durability and event replayability.
   - **Ping Types (4-Tier Lifecycle)**: Start-of-Trip, 4-Minute Batch, End-of-Trip, Emergency.
   - **Ingestion Quality Agent**: A deterministic Python router that scrubs normal telemetry (GPS, speed) before it hits the database.
   - **PII Scrubber Agent**: An AI agent that *only* receives and cleans user-generated content (e.g., driver feedback/appeals) before database persistence.

3. **Orchestrator Execution**:
   - **LangGraph**: Used as the primary mechanism for cyclical agent workflow tracking.
   - **Batch Evaluation Loop**: The Orchestrator receives 4-Minute Batch strings but runs a fast, low-cost evaluation node. If no immediate action is needed, the batch is simply written to the database and execution terminates (Discard flow), saving tokens and latency.

4. **Internal State & Queuing**:
   - **Redis + Celery**: Used exclusively for internal asynchronous task routing and tracking active vs zombie trips within the middleware layer.

5. **Context Enrichment**:
   - **Model Context Protocol (MCP)**: The Context Enrichment Agent uses MCP to fetch external context (weather, route mapping, speed limits). It is structured as a shared Tool/Service called on-demand by other agents (like Behavior or Safety) rather than interacting as a conversational peer. Must meet an SLA of < 2 seconds.

## Directives for AI Agents

- **Always verify constraints**: Before scaffolding new services, confirm they fit within the Python FastAPI + LangGraph boundary.
- **Do not introduce microservices**: The project strictly prohibits microservices for core booking/fleet logic.
- **Respect Database Boundaries**: Use a single PostgreSQL database but maintain strict schema boundaries. No cross-schema foreign keys.
