# ADR-002: Replace Apache Kafka with Redis + Celery for Event Ingestion & Task Queueing

**Date:** 2026-03-19
**Status:** Accepted
**Deciders:** TraceData Capstone Team (Dinesh, Jenige, Sreeraj, Zhicheng)

## Context

The primary objective of TraceData's messaging architecture is to **demonstrate Event-Driven Architecture (EDA) as a core system design pattern** — specifically: priority-based event routing, asynchronous decoupling of producers and consumers, and event replay. This is the academic and professional learning goal of the SWE5008 capstone.

The original design listed **Apache Kafka** as the streaming backbone, with **Redis + Celery** for internal async tasks. This created an unnecessary two-layer model:

```
IoT Vehicles → Kafka (4 topics) → FastAPI Consumer → Celery (internal tasks) → PostgreSQL
```

**Redis + Celery already implements EDA in full** — priority queues, async workers, decoupled producers/consumers, and Redis Streams for replay. Kafka adds operational complexity (broker cluster, Zookeeper/KRaft, topic management, consumer group rebalancing) that serves no additional EDA learning value at this project's scale (≤10,000 simulated vehicles, single-region).

## Decision

**Remove Apache Kafka entirely.** Use **Redis + Celery** as the single EDA layer, with **Redis Streams** for event replay.

The ingestion pipeline:

```
IoT Vehicles → FastAPI (POST /api/v1/telemetry) → Celery Task Router → Priority Queues → Agents → PostgreSQL
                                                               │
                                                         Redis Streams (XADD)
                                                         (replay / audit log)
```

**Priority Queues (Celery):**

| Queue            | Priority | Ping Type          | SLA          |
| :--------------- | :------- | :----------------- | :----------- |
| `queue.critical` | Highest  | Emergency Ping     | < 5 seconds  |
| `queue.high`     | High     | Harsh events       | < 10 seconds |
| `queue.medium`   | Medium   | Standard telemetry | < 30 seconds |
| `queue.low`      | Low      | Analytics          | Best effort  |

This gives us all the EDA properties we need to demonstrate:
- **Async decoupling** — FastAPI (producer) is fully decoupled from Agent workers (consumers)
- **Priority routing** — `queue.critical` pre-empts all lower queues; Emergency Pings are never delayed by analytics backlog
- **Event replay** — Redis Streams (`XADD`/`XREAD`) allow re-processing of any event for debugging or auditing
- **Observable workers** — Celery Flower dashboard provides real-time visibility into queue depth and task state

## Rationale

### Why Redis + Celery proves EDA sufficiently

| Factor | Kafka | Redis + Celery |
| :--- | :--- | :--- |
| **Operational complexity** | Requires broker cluster + Zookeeper/KRaft, topic management, consumer group coordination | Single Redis container; Celery workers are standard Python processes |
| **Team capacity** | Significant ops burden for 4-person academic team | Near-zero additional ops overhead — Redis already deployed |
| **Project scale** | Designed for millions of events/sec distributed | Appropriate for ≤10,000 simulated vehicles, single-region |
| **Priority routing** | Requires separate topics + consumer groups to simulate priority | Native `CELERY_TASK_ROUTES` + `task_routes` priority config |
| **Latency** | ~5–10ms (broker round-trip) | ~1–2ms (in-memory) |
| **Replay / durability** | Log compaction, configurable retention | Redis Streams with AOF/RDB persistence achieves the same for this scale |

### What we lose

- **Infinite log retention**: Kafka can retain events indefinitely. Redis Streams are bounded by memory/MAXLEN setting. **Mitigation**: All events are persisted to PostgreSQL on ingest; Streams serve as a short-term audit buffer.
- **Fan-out at partition scale**: Kafka's consumer groups support massive parallel fan-out. **Mitigation**: Not needed at ≤10,000 vehicles; Celery worker concurrency is sufficient.

## Consequences

- **Single messaging layer reduces operational surface area.**
- **Eliminates a Docker service (Kafka + Zookeeper), simplifying `docker-compose.yml`.**
- **Redis already in use for conversation state — no new infrastructure.**
- **Celery priority queues provide a cleaner API for the 4-level priority model.**
- **Redis Streams MAXLEN must be configured to prevent unbounded memory growth in long-running simulations (recommended: `MAXLEN ~= 1,000,000` events with `~` approximate trimming).**
- **If the project ever scales to 500,000+ vehicles or requires multi-region fan-out, re-introducing Kafka or migrating to AWS SQS/SNS should be reconsidered.**

## References

- [FR-1 — Telemetry Ingestion & Lifecycle Management](../01-project-documents/02-project-requirements.md#31-telemetry-ingestion--lifecycle-management-fr-1)
- [Tech Stack — Project Proposal](../01-project-documents/01-project-proposal.md#technology-stack)
- [Celery Priority Queues Documentation](https://docs.celeryq.dev/en/stable/userguide/routing.html#task-priority)
- [Redis Streams Introduction](https://redis.io/docs/latest/develop/data-types/streams/)
