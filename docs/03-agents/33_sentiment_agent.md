# Sentiment Agent

## Overview

The Sentiment Agent processes end-of-trip `driver_feedback` text and produces
an embedding-driven emotional analysis result for the trip.

Primary question:

**"What is the driver's emotional condition after this trip?"**

---

## Implemented Flow

`driver_feedback -> orchestrator -> sentiment -> sentiment_ready -> orchestrator -> support`

---

## Responsibilities

- Analyze feedback text from `driver_feedback`.
- Score the feedback against anchor embeddings stored in Postgres + pgvector.
- Retrieve recent same-driver feedback history from `sentiment_schema.feedback_sentiment`.
- Compute window averages, trend, and an operational `risk_level`.
- Persist sentiment result in `sentiment_schema.feedback_sentiment`.
- Write `trip:{trip_id}:sentiment_output` for downstream consumption.
- Trigger synthetic `sentiment_ready` for orchestrator handoff to support.

---

## Runtime Components

| Layer | Responsibility |
|------|----------------|
| Celery task | `tasks.sentiment_tasks.analyse_feedback` runs `SentimentAgent.run(IntentCapsule)` |
| Agent base | Scoped Redis read via capsule keys, executes analysis, writes output, releases lock, publishes completion |
| LangGraph pipeline | `score_current -> load_history -> analyze_window -> explain -> assemble_output` |
| Repository | `SentimentRepository` writes sentiment records to `sentiment_schema` |
| Follow-up helper | `schedule_sentiment_ready_if_success` inserts synthetic `sentiment_ready` and enqueues it to processed queue |

---

## Redis Keys

### Inputs (warmed by orchestrator)

- `trips:{trip_id}:sentiment:current_event`
- `trips:{trip_id}:sentiment:trip_context`

### Sentiment output

- Key: `trip:{trip_id}:sentiment_output`
- Type: String (JSON)
- Consumer: Orchestrator, then Support Agent

### Downstream support output

- Key: `trip:{trip_id}:support_output`
- Type: String (JSON)
- Consumer: Orchestrator and downstream app flows

---

## PostgreSQL

**Schema:** `sentiment_schema`

| Table | Purpose |
|------|---------|
| `feedback_sentiment` | Stores trip-level sentiment record (`trip_id`, `driver_id`, `feedback_text`, `feedback_embedding`, `sentiment_score`, `sentiment_label`, `analysis`) |
| `emotion_anchor_embeddings` | Stores reusable emotion anchor texts and their pgvector embeddings for similarity scoring |

Orchestrator synthetic follow-up event is persisted in `pipeline_events` as
`event_type='sentiment_ready'`.

---

## Event Matrix Contract

- `driver_feedback` -> action `SENTIMENT` -> dispatch `sentiment`
- `sentiment_ready` -> action `SUPPORT` -> dispatch `driver_support`
