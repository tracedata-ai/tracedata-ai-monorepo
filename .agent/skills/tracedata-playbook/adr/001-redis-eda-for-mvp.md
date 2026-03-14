# ADR 001: Redis vs Kafka for Event-Driven Architecture (MVP)

## Status
Accepted

## Context
The TraceData platform requires an Event-Driven Architecture (EDA) to decouple real-time telemetry ingestion from heavy AI processing (XGBoost scoring, GenAI coaching). The initial consideration was Apache Kafka, the industry standard for high-throughput stream processing.

## Decision
We have opted to use **Redis 7 (Pub/Sub) + Celery** as the message broker and task runner for the 15-day MVP sprint.

## Trade-off Matrix

| Feature | Redis (Chosen) | Apache Kafka |
| :--- | :--- | :--- |
| **Complexity** | Low (Already in stack) | High (Zookeeper, Broker configs) |
| **Persistence** | In-memory (Ephemeral) | Disk-based (Durable) |
| **Delivery** | Fire-and-forget / At-most-once | Guaranteed / At-least-once |
| **Scalability** | High (for MVP loads) | Extreme (Terabytes/sec) |
| **Replay** | No | Yes (Event Sourcing) |

## Justification
For a 15-day development timeline, the operational overhead of Kafka (ZooKeeper management, Docker complexity) presents a significant risk. Redis satisfies the core EDA requirement—loose coupling and autonomous agent execution—while maintaining rapid development velocity. 

**This is a pragmatic engineering decision:** The architecture is designed to be "broker-agnostic," allowing for a seamless swap to Kafka in Phase 2 for production-grade persistence and event replay.

## Consequences
- **Positive**: Simplified CI/CD, lower latency for ingestion, faster iteration.
- **Negative**: No built-in event replay; if a consumer is down, messages are lost unless retry logic is implemented in Celery.
