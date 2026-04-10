# Pipeline Event Locking — Optimistic-Lease Hybrid

**Table:** `pipeline_events`  
**Implemented in:** [`common/db/repositories/events_repo.py`](../../backend/common/db/repositories/events_repo.py)  
**ORM model:** [`common/models/orm.py · EventORM`](../../backend/common/models/orm.py)

---

## Overview

`pipeline_events` uses an **optimistic-lease hybrid** locking strategy to coordinate work between the Orchestrator and Celery agents without holding long-lived database locks.

| Property | Value |
|---|---|
| Lock type | Conditional UPDATE (compare-and-swap) |
| Lock holder | `locked_by VARCHAR(50)` |
| Lease timer | `locked_at TIMESTAMP` |
| Retry tracking | `retry_count INTEGER` |
| State machine | `status VARCHAR(20)` |
| Watchdog TTL | 10 minutes (configurable) |

### Why a hybrid?

A pure **pessimistic** lock (`SELECT FOR UPDATE`) holds a Postgres row lock for the entire agent runtime — seconds to minutes. Under load this serialises the entire pipeline.

A pure **optimistic** lock (version counter + retry-on-conflict) has no safety net: if the agent crashes mid-flight the version is never incremented and the row is stuck forever.

The hybrid takes the best of both:

- **Optimistic acquire** — a single conditional `UPDATE` acts as a compare-and-swap. No row lock is held while the agent runs. Two concurrent orchestrators racing on the same row: exactly one gets `rowcount == 1`.
- **Pessimistic hold** — once acquired, the row is exclusively marked `status='processing'`. Nothing else can pick it up during agent execution.
- **Watchdog safety net** — a background sweep resets any `status='processing'` row whose `locked_at` has expired, covering crashes and hangs.

---

## Row Schema (locking fields only)

```sql
status       VARCHAR(20)  DEFAULT 'received'   -- state machine key
locked_by    VARCHAR(50)  NULLABLE             -- who holds the lease
locked_at    TIMESTAMP    NULLABLE             -- when the lease was taken
retry_count  INTEGER      DEFAULT 0            -- incremented on each failure
processed_at TIMESTAMP    NULLABLE             -- set on successful completion
```

---

## State Machine

```mermaid
stateDiagram-v2
    direction LR

    [*] --> received : Ingestion writes event

    received --> processing : acquire_lock()\nCAS UPDATE succeeds

    processing --> processed : release_lock()\nAgent completed OK

    processing --> failed : fail_event()\nCelery task exhausted retries

    processing --> received : watchdog_reset_stuck()\nlocked_at expired (TTL 10 min)

    processing --> locked : lock_for_hitl()\nFleet manager escalation

    failed --> received : manual reset\nor retry policy

    locked --> [*] : fleet manager resolves\n(watchdog excluded)
```

> **`locked` is a terminal escalation state.** The watchdog explicitly excludes it — only a human fleet manager action can exit HITL.

---

## Lock Acquire — Optimistic CAS

The acquire is a single atomic `UPDATE` with a `WHERE` guard. No `SELECT FOR UPDATE`, no advisory lock.

```mermaid
sequenceDiagram
    participant O as Orchestrator
    participant DB as PostgreSQL

    O->>DB: UPDATE pipeline_events<br/>SET status='processing',<br/>    locked_by='orchestrator',<br/>    locked_at=now()<br/>WHERE device_event_id = :id<br/>AND status = 'received'<br/>AND locked_by IS NULL

    alt rowcount == 1
        DB-->>O: Lock acquired ✓
        O->>O: Dispatch to Celery
    else rowcount == 0
        DB-->>O: Lock failed ✗<br/>(already locked or wrong status)
        O->>O: Back off, skip event
    end
```

**Why this is safe under concurrency:** PostgreSQL executes the conditional `UPDATE` atomically within its MVCC engine. Even if two orchestrator processes submit the identical statement at the same millisecond, the database guarantees exactly one wins — the other sees `rowcount == 0`.

---

## Lock Release — Happy Path

```mermaid
sequenceDiagram
    participant C as Celery Agent
    participant DB as PostgreSQL

    C->>C: Execute agent logic
    C->>DB: UPDATE pipeline_events<br/>SET status='processed',<br/>    locked_by=NULL,<br/>    locked_at=NULL,<br/>    processed_at=now()<br/>WHERE device_event_id = :id<br/>AND status = 'processing'
    DB-->>C: Lock released ✓
```

The `AND status = 'processing'` guard prevents a late-arriving release from accidentally re-processing an event the watchdog already reset.

---

## Failure Path — Agent Exhausted Retries

```mermaid
sequenceDiagram
    participant C as Celery Agent
    participant DB as PostgreSQL

    C->>C: Execute agent logic
    C--xC: Exception raised
    C->>C: Celery retry (exp backoff,<br/>max 3 attempts)
    C--xC: All retries exhausted

    C->>DB: UPDATE pipeline_events<br/>SET status='failed',<br/>    locked_by=NULL,<br/>    locked_at=NULL,<br/>    retry_count = retry_count + 1<br/>WHERE device_event_id = :id
    DB-->>C: Row marked failed
```

`status='failed'` is **not** automatically retried. It requires a manual reset or an explicit retry policy. This prevents poison-pill events from looping indefinitely.

---

## Watchdog — Crash Recovery

The watchdog runs periodically. It finds any `status='processing'` row whose lease has expired and resets it back to `received` so the orchestrator can re-acquire it on the next poll cycle.

```mermaid
sequenceDiagram
    participant W as Watchdog
    participant DB as PostgreSQL
    participant O as Orchestrator

    loop Every N minutes
        W->>DB: UPDATE pipeline_events<br/>SET status='received',<br/>    locked_by=NULL,<br/>    locked_at=NULL<br/>WHERE status='processing'<br/>AND locked_by='orchestrator'<br/>AND locked_at < now() - INTERVAL '10 minutes'<br/>RETURNING device_event_id, trip_id

        alt Stuck rows found
            DB-->>W: [device_event_id, trip_id, ...]
            W->>W: Log warning: watchdog_recovered
        else No stuck rows
            DB-->>W: (empty)
        end
    end

    O->>DB: Poll for status='received'
    DB-->>O: Recovered event visible again
    O->>O: Re-acquire lock, re-dispatch
```

> **HITL exclusion:** The watchdog `WHERE` clause only targets `locked_by='orchestrator'`. Rows in `status='locked'` (HITL) have `locked_by=NULL` and are therefore invisible to the watchdog — they can never be silently reset.

---

## HITL Escalation

When a fleet manager escalates an event for human review, `lock_for_hitl()` sets a special terminal state.

```mermaid
stateDiagram-v2
    direction LR

    processing --> locked : lock_for_hitl()\nlocked_by = NULL\nlocked_at = NULL

    note right of locked
        Watchdog excluded:
        WHERE locked_by = 'orchestrator'
        does NOT match this row.
        Only fleet manager can resolve.
    end note
```

Setting `locked_by=NULL` on a `locked` row is intentional — it makes the watchdog's `AND locked_by='orchestrator'` guard fail, creating a hard exclusion with no special-case code in the watchdog itself.

---

## End-to-End Pipeline Flow

```mermaid
flowchart TD
    A[Telemetry Device] -->|raw packet| RB[Redis Buffer\ntelemetry:truck:buffer]
    RB -->|pop| ING[Ingestion Sidecar\n7-step pipeline]
    ING -->|INSERT status=received| PE[(pipeline_events)]
    ING -->|push TripEvent| RP[Redis Processed Queue\ntelemetry:truck:processed]

    RP -->|pop| ORC[Orchestrator]
    ORC -->|acquire_lock CAS UPDATE| PE
    ORC -->|rowcount==1| WARM[Cache Warming\nRedis]
    WARM --> DISP[Dispatch to Celery]

    DISP --> SA[Safety Agent\ntd:agent:safety]
    DISP --> SC[Scoring Agent\ntd:agent:scoring]
    DISP --> SU[Support Agent\ntd:agent:support]
    DISP --> SE[Sentiment Agent\ntd:agent:sentiment]

    SA -->|release_lock / fail_event| PE
    SC -->|release_lock / fail_event| PE
    SU -->|release_lock / fail_event| PE
    SE -->|release_lock / fail_event| PE

    WD[Watchdog\nperiodic sweep] -->|reset expired leases| PE

    style PE fill:#1e3a5f,color:#fff
    style WD fill:#7b2d00,color:#fff
    style ORC fill:#1a4731,color:#fff
```

---

## Concurrency Guarantee — Two Orchestrators Racing

```mermaid
sequenceDiagram
    participant O1 as Orchestrator A
    participant O2 as Orchestrator B
    participant DB as PostgreSQL

    Note over O1,O2: Both pop the same TripEvent from Redis processed queue

    par
        O1->>DB: UPDATE ... WHERE status='received' AND locked_by IS NULL
    and
        O2->>DB: UPDATE ... WHERE status='received' AND locked_by IS NULL
    end

    DB-->>O1: rowcount = 1 (wins)
    DB-->>O2: rowcount = 0 (loses)

    O1->>O1: Dispatch to Celery ✓
    O2->>O2: Skip — lock not acquired ✗
```

Postgres serialises the two `UPDATE` statements at the storage level. The race is resolved inside the database engine — no application-level mutex, no advisory lock, no retries needed.

---

## `pipeline_trips` State Machine

`pipeline_trips` tracks the higher-level trip lifecycle. It is updated by the Orchestrator as key events arrive, independently of the per-event row locking above.

```mermaid
stateDiagram-v2
    direction LR

    [*] --> active : start_of_trip received\ncreate_trip()

    active --> scoring_pending : end_of_trip received\nupdate_trip(status)

    scoring_pending --> coaching_pending : coaching_ready event\n(Scoring Agent output)

    coaching_pending --> complete : all agents done\ncapsule_closed = true

    active --> failed : agent error\nmax retries exhausted

    active --> locked : HITL escalation\nwatchdog excluded
```

---

## Key Invariants

| Invariant | Enforced by |
|---|---|
| Only one agent runs per event at a time | CAS `UPDATE` — `rowcount == 1` |
| Crashed agents don't leave rows stuck forever | Watchdog TTL reset |
| HITL rows are never silently reset | `locked_by=NULL` excludes watchdog |
| Late release can't re-process a watchdog-reset row | `AND status='processing'` guard on release |
| Poison-pill events don't loop indefinitely | `status='failed'` requires manual intervention |
| Duplicate events are idempotent | `device_event_id UNIQUE` constraint + sidecar dedup check |
