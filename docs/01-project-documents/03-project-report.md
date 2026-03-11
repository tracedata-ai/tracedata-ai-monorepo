# TraceData: Project Execution Report & Specifications
## SWE5008 Capstone Project

This document consolidates the detailed technical specifications for the TraceData Multi-Agent AI Middleware, including the Agent Topology and the Telematics Data Shape.

---

## Part 1: Agent Topology Specifications

TraceData relies on a **Multi-Agent AI Middleware Layer** (built with Python, FastAPI, and LangGraph) to analyze telemetry data, score trips, ensure fairness, and manage driver feedback.

The topology is designed to prevent runaway token costs and execution bottlenecks by strictly distinguishing between deterministic routers, fast-evaluation loops, and heavy generative AI agents.

### 1. Ingestion & Pre-Processing Agents

#### 1. Ingestion Quality Agent (Deterministic Router)
- **Type**: Deterministic Python Service (Not LLM-based)
- **Role**: Sits between Kafka consumers and the database. Receives dual sources: structured telemetry and unstructured driver inputs. Handles 4-10 minute batch pings and real-time critical bypass pings.
- **Execution**: Scrubs standard structured telemetry (GPS, Speed, RPM) deterministically and routes it directly to PostgreSQL.
- **Handoff**: Extracts any free-text `user_input` and forwards it exclusively to the PII Scrubber Agent.

#### 2. PII Scrubber Agent
- **Type**: Generative AI / NLP
- **Role**: Sanitizes user-generated text (Appeals, Feedback) to remove Personally Identifiable Information (PII) before it is committed to the database.
- **Constraints**: Only invoked when the Ingestion Quality Agent detects text payloads, preserving system throughput.

### 2. Core Orchestration

#### 3. Orchestrator Agent
- **Type**: LangGraph State Machine (Router/Evaluator)
- **Role**: The central dispatcher for the system. Once data is pre-processed, the Orchestrator evaluates the event type to determine the execution path.
- **4-Minute Batch Handling**: Runs a fast, low-cost evaluation node ("Are critical actions needed?"). If no, execution terminates (persists to DB). If yes, routes to appropriate sub-agents. Aggregates data to build an encouragement profile.
- **End-of-Trip Handling**: Routes the payload to the Behavior Agent to initiate scoring.
- **Feedback/Appeals**: Uses LLM-based reasoning on unstructured text to route to the Sentiment and Advocacy agents.

### 3. Analytical & Action Agents

#### 4. Behavior Agent
- **Type**: Predictive ML (XGBoost) + XAI (AIF360, SHAP)
- **Role**: Triggered at the end of a trip. Calculates the safety score (0-100) using XGBoost.
- **Fairness Loop**: Applies AIF360 Reweighting to ensure the Statistical Parity Difference (SPD) remains < 0.5. Generates SHAP/LIME feature importance values.
- **Handoff**: Passes the raw score and explanation context to the Coaching Agent.

#### 5. Safety Agent
- **Type**: Deterministic Evaluator + Tool Caller
- **Role**: Triggered by an `Emergency Ping` from the dedicated Critical Events pipe.
- **Action**: Quickly analyzes the critical event (e.g., hard brake > 0.6g) against enriched context (via Context Agent).
- **Output**: Executes a multi-level intervention strategy: Level 1 (App Notification), Level 2 (Formal Message), or Level 3 (Direct Call/Escalation to FM).

#### 6. Sentiment Agent
- **Type**: Generative AI / NLP
- **Role**: Analyzes the emotional trajectory of a driver based on a rolling window of their last 5 feedback submissions.
- **Output**: Calculates a `risk_level` (0-1). If > 0.7, flags the driver for imminent burnout, alerting the Fleet Manager and updating the `sentiment_trends` table.

#### 7. Advocacy Agent
- **Type**: Generative AI (Reasoning Loop)
- **Role**: Processes formal driver appeals. Can access historical trip logs, LIME explanations, and rules of conduct.
- **Output**: Drafts an initial response to the driver's dispute. For high-complexity disputes, it pauses and escalates the graph to a human Fleet Manager for review.

#### 8. Coaching Agent
- **Type**: Generative AI (Content Creator)
- **Role**: Synthesizes the trip score from the Behavior Agent and the driver's current emotional state from the Sentiment Agent.
- **Output**: Generates highly personalized, actionable coaching points tailored to the driver's emotional context (Encouraging, Supportive, Directive) ensuring no two coaching outputs are identical.

### 4. Tooling Layer

#### Context Enrichment Agent (MCP Tool)
- **Type**: Model Context Protocol (MCP) Service
- **Role**: A shared, high-speed Tool Node used by the other agents (primarily Behavior, Safety, and Orchestrator).
- **Action**: Translates coordinates and timestamps into rich contextual metadata (road type, legal speed limit, hotspot risk, weather).
- **Constraints**: Must return payloads in < 2 seconds. Fails over gracefully to default mappings to prevent blocking the graph.

---

## Part 2: Telematics Data Shape & Schema Specifications

### 1. Schema Design: The Flat Schema
The flat, generic event schema was deliberately chosen over a stratified (typed/inheritance) schema to optimize for the AI system’s specific needs—prioritizing Explainable AI (XAI)/LIME and fairness audits.

#### Key Justifications:
- **XAI/LIME & Fairness Optimization**: All features are flattened into a single `details` dictionary, enabling uniform feature ranking and easy "apples-to-apples" comparison for fairness audits.
- **Distributed Processing Simplicity**: A single ubiquitous schema simplifies integration with Kafka and downstream serverless/middleware functions, eliminating union type overhead and discriminator logic complexity.
- **Extensibility & API Evolution**: Adding new event fields is non-breaking (forward-compatible), as new fields are simply inserted into the details dictionary.
- **Negligible Cost Tradeoffs**: The slight increase in network processing and storage cost (an extra ~100-200 bytes per event) is irrelevant at the current scale, minimized by compression, and outweighed by massive AI benefits.
- **Sparse Fields & Sparsity**: The database tables and JSON schemas are highly scalable. Any event-specific fields not relevant to the current `event_type` or lacking valid data from the device are simply omitted from the payload (not sent) to save bandwidth while guaranteeing a uniform columnar structure for fast querying.
- **Runtime Type Safety**: While compile-time type safety is lost with a flat schema, this is mitigated by robust runtime Pydantic validation upon ingestion, achieving equal safety via a different mechanism.

### 2. General JSON Structure
The telematics payload sent to the ingestion layer follows this flat structure:

```json
{
  "event_id": "<global unique event id>",
  "device_event_id": "<id as reported by device>",
  "trip_id": "<trip identifier>",
  "driver_id": "<driver identifier>",
  "truck_id": "<vehicle identifier>",
  "event_type": "<event kind, e.g. speeding | harsh_brake | collision>",
  "category": "<logical bucket, e.g. speed_compliance | harsh_event | critical>",
  "priority": "<severity routing, e.g. critical | high | medium | low>",
  "timestamp": "<ISO8601 UTC time of event>",
  "offset_seconds": "<seconds from trip/batch start or null>",
  "location": {
    "lat": "<latitude float>",
    "lon": "<longitude float>"
  },
  "media": {
    "video_url": "<s3_url_15s_clip>", // Omitted if no video
    "image_url": "<s3_url_snapshot>"  // Omitted if no image
  },
  "schema_version": "event_v<version>",
  "details": {
    // type-specific fields, depending on event_type
  }
}
```

### 3. Event Categories and Priorities

#### Priority Escalation Levels
1. **Critical** → `emergency_services` (e.g., Immediate 911 call or severe accident dispatch)
2. **High** → `fleet_manager_alert` / `coaching` (HITL - Human in the Loop recommended)
3. **Medium** → `coaching` (Generated coaching feedback)
4. **Low** → `analytics` only

#### Event Taxonomy
| Event Type | Category | Priority | Escalation Action |
| --- | --- | --- | --- |
| `collision` | `critical` | **Critical** | `emergency_services` |
| `rollover` | `critical` | **Critical** | `emergency_services` |
| `vehicle_offline` | `critical` | **High** | `fleet_manager_alert` |
| `harsh_brake` | `harsh_event` | **High** | `coaching` |
| `hard_accel` | `harsh_event` | **High** | `coaching` |
| `harsh_corner` | `harsh_event` | **High** | `coaching` |
| `driver_feedback` | `driver_feedback` | **High/Medium** | Agent Routing |
| `speeding` | `speed_compliance` | **Medium** | `coaching` |
| `excessive_idle` | `idle_fuel` | **Low** | `coaching` |
| `normal_operation` | `normal_operation` | **Low** | `analytics` |

### 4. Telematics Ping Load & Trigger Calculation

To support the flat schema effectively, TraceData classifies ingestions into four explicit payload events: 

#### 1. Emergency Ping
*Immediate critical event response (911 dispatch)*
- **Trigger (Hardware/Device Detection)**:
  - Airbag deployment (CAN bus signal)
  - Severe impact (`g_force_magnitude > 2.5`)
  - Rollover (vehicle orientation `> 45°` roll)
  - Manual SOS button pressed
- **Data Content**:
  - Critical event identifier (collision or rollover)
  - Raw sensor data (pre/post-impact buffer)
  - **Video evidence**: 15s pre/post-incident dashcam clip uploaded to AWS S3 (provided as `video_url`)
  - Voice recording (cabin audio, injury detection)
  - High-precision GPS coordinates

#### 2. Normal Ping (Every 4 minutes)
*Regular heartbeat collating events and safe driving checkpoints*
- **Trigger**: Timer fires every 4 minutes during an active trip.
- **Data Content**:
  - **Incident-Driven (Threshold triggered)**:
    *(Note: Any harsh event triggers a 15s pre/post-incident video/photo upload to AWS S3, provided as URLs in the ping data)*
    - `speeding` (>speed_limit for >30s)
    - `harsh_brake` (g_force < -0.7)
    - `hard_accel` (g_force > 0.75)
    - `harsh_corner` (lateral g_force > 0.8)
    - `excessive_idle` (engine running, no movement >5m)
    - `vehicle_offline` (no GPS >60s)
  - **Fixed 30-Second Normal Operation Checkpoints**:
    - Generates a `normal_operation` event every 30 seconds if no incident occurred.
    - Enables fair ML normalization: "X% of the trip was verifiably safe."

#### 3. Start of Trip Ping
*Marks trip boundary, confirms driver readiness, and captures contextual baseline metrics*
- **Trigger**: Driver manually starts the trip via app, OR auto-detected (ignition on + device connected).
- **Data Content**:
  - Trip metadata (start time, vehicle state)
  - Driver confirmation (logged in identity)
  - Vehicle readiness (all systems OK checklist)
  - Baseline metrics (fuel level, odometer reading)

#### 4. End of Trip Ping
*Complete summary initiating ML scoring and Agentic evaluation*
- **Trigger**: Driver manually marks trip complete via app, OR auto-detected (ignition off + idle > 200s).
- **Data Content**:
  - Full trip duration + aggregated metrics (total distance, fuel consumed, average speed)
  - Complete holistic event list
  - Safety percentage (`safe_checkpoints` / `total_checkpoints`)
  - Triggers the `Behavior Agent` for ML scoring and fairness audits.
