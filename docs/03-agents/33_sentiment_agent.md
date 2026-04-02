# Sentiment Agent

The Sentiment Agent is TraceData's feedback analyzer for post-trip driver text.
It runs on `driver_feedback` events and persists sentiment results to
`sentiment_schema`, then hands control back to the orchestrator for follow-up
dispatch.

---

## Product role

The Sentiment Agent answers:

1. **"What is the emotional signal in this feedback?"**
2. **"Should this feedback trigger a downstream support action?"**

It does not write coaching narratives itself. Support decisions remain owned by
the orchestrator + Support Agent chain.

---

## Trigger and handoff flow

1. Ingestion stores `driver_feedback` in `pipeline_events` and pushes the clean
   event to `telemetry:{truck_id}:processed`.
2. Orchestrator routes `driver_feedback` to **Sentiment** (Event Matrix action
   is `SENTIMENT`).
3. Orchestrator warms sentiment keys and dispatches
   `tasks.sentiment_tasks.analyse_feedback`.
4. Sentiment analyzes feedback and writes `trip:{trip_id}:sentiment_output` +
   completion pub/sub event.
5. After successful sentiment run, the worker enqueues synthetic
   **`sentiment_ready`**.
6. Orchestrator consumes `sentiment_ready`, warms Support context including
   `sentiment_output`, and dispatches Support.

This makes driver feedback processing explicitly two-wave:

`driver_feedback -> sentiment -> sentiment_ready -> orchestrator -> support`

---

## Runtime architecture

| Layer | Responsibility |
|--------|----------------|
| **Celery** | `tasks.sentiment_tasks.analyse_feedback` invokes `SentimentAgent.run(IntentCapsule)` |
| **`TDAgentBase`** | Scoped Redis reads via `read_keys`, executes `_execute`, stores `trip:{trip_id}:sentiment_output`, releases lock, publishes completion |
| **`SentimentRepository`** | Writes only to `sentiment_schema` tables |
| **Sentiment follow-up helper** | `schedule_sentiment_ready_if_success` inserts synthetic `sentiment_ready` and pushes to `telemetry:{truck_id}:processed` |

---

## Redis and warming

### Warmed input (orchestrator -> capsule `read_keys`)

For `driver_feedback` (event-driven warming):

- `trips:{trip_id}:sentiment:current_event`
- `trips:{trip_id}:sentiment:trip_context`

For `sentiment_ready` (post-sentiment support warming):

- `trips:{trip_id}:support:trip_context` (contains `sentiment_output`)

### Output and completion

- `trip:{trip_id}:sentiment_output` (SET JSON)
- `trip:{trip_id}:events` (PUBLISH completion payload)

---

## Current output shape

The sentiment worker currently returns a compact result:

```json
{
  "status": "success",
  "sentiment": "neutral",
  "sentiment_id": "UUID",
  "trip_id": "TRP-..."
}
```

This contract is intentionally minimal for now; Support consumes the warmed
`sentiment_output` snapshot during `sentiment_ready`.

---

## PostgreSQL

**Schema:** `sentiment_schema`

| Table | Written by | Content |
|-------|------------|---------|
| `driver_feedback_analysis` | `SentimentRepository` | Feedback text + sentiment score/label + analysis metadata |

Orchestrator-side synthetic follow-up events are written to `public.pipeline_events`
as `event_type='sentiment_ready'`.

---

## Event matrix contract (implemented)

- `driver_feedback` -> action `SENTIMENT` -> dispatch `sentiment`
- `sentiment_ready` -> action `SUPPORT` -> dispatch `driver_support`

This guarantees all driver feedback is analyzed by Sentiment first, then
re-evaluated by Orchestrator for downstream support flow.

---

## Limitations

- Current sentiment classifier is a simple keyword heuristic (not full NLP model).
- Sentiment output is compact; richer theme extraction is not yet persisted.
- Support handoff is currently deterministic via `sentiment_ready` mapping.
