# TraceData: Agentic AI Middleware Specifications

## SWE5008 Capstone Project

## 1. Overview of the Agent Topology

TraceData relies on a **Multi-Agent AI Middleware Layer** (built with Python, FastAPI, and LangGraph) to analyze telemetry data, score trips, ensure fairness, and manage driver feedback.

The topology is designed to prevent runaway token costs and execution bottlenecks by strictly distinguishing between deterministic routers, fast-evaluation loops, and heavy generative AI agents.

## 2. Ingestion & Pre-Processing Agents

### 1. Ingestion Quality Agent (Deterministic Router)

- **Type**: Deterministic Python Service (Not LLM-based)
- **Role**: Sits between Kafka consumers and the database. Parses incoming payloads (Start, Batch, End, Emergency).
- **Execution**: Scrubs standard structured telemetry (GPS, Speed, RPM) using strict validation rules and routes the sanitized data directly to PostgreSQL.
- **Handoff**: Extracts any free-text `user_input` and forwards it exclusively to the PII Scrubber Agent.

### 2. PII Scrubber Agent

- **Type**: Generative AI / NLP
- **Role**: Sanitizes user-generated text (Appeals, Feedback) to remove Personally Identifiable Information (PII) before it is committed to the database.
- **Constraints**: Only invoked when the Ingestion Quality Agent detects text payloads, preserving system throughput.

## 3. Core Orchestration

### 3. Orchestrator Agent

- **Type**: LangGraph State Machine (Router/Evaluator)
- **Role**: The central dispatcher for the system. Once data is pre-processed, the Orchestrator evaluates the event type to determine the execution path.
- **4-Minute Batch Handling**: Runs a fast, low-cost evaluation node ("Are critical actions needed?"). If no, execution terminates (persists to DB). If yes, routes to appropriate sub-agents.
- **End-of-Trip Handling**: Routes the payload to the Behavior Agent to initiate scoring.
- **Feedback/Appeals**: Routes to the Sentiment and Advocacy agents.

## 4. Analytical & Action Agents

### 4. Behavior Agent

- **Type**: Predictive ML (XGBoost) + XAI (AIF360, SHAP)
- **Role**: Triggered at the end of a trip. Calculates the safety score (0-100) using XGBoost.
- **Fairness Loop**: Applies AIF360 Reweighting to ensure the Statistical Parity Difference (SPD) remains < 0.5. Generates SHAP/LIME feature importance values.
- **Handoff**: Passes the raw score and explanation context to the Coaching Agent.

### 5. Safety Agent

- **Type**: Deterministic Evaluator + Tool Caller
- **Role**: Triggered by an `Emergency Ping` or a critical flag from a `4-Minute Batch`.
- **Action**: Quickly analyzes the critical event (e.g., hard brake > 0.6g) against enriched context (via Context Agent).
- **Output**: Generates real-time alerts for the Fleet Manager dashboard via external notification services if the anomaly is severe.

### 6. Sentiment Agent

- **Type**: Generative AI / NLP
- **Role**: Analyzes the emotional trajectory of a driver based on a rolling window of their last 5 feedback submissions.
- **Output**: Calculates a `risk_level` (0-1). If > 0.7, flags the driver for imminent burnout, alerting the Fleet Manager and updating the `sentiment_trends` table.

### 7. Advocacy Agent

- **Type**: Generative AI (Reasoning Loop)
- **Role**: Processes formal driver appeals. Can access historical trip logs, LIME explanations, and rules of conduct.
- **Output**: Drafts an initial response to the driver's dispute. For high-complexity disputes, it pauses and escalates the graph to a human Fleet Manager for review.

### 8. Coaching Agent

- **Type**: Generative AI (Content Creator)
- **Role**: Synthesizes the trip score from the Behavior Agent and the driver's current emotional state from the Sentiment Agent.
- **Output**: Generates highly personalized, actionable coaching points tailored to the driver's emotional context (Encouraging, Supportive, Directive) ensuring no two coaching outputs are identical.

## 5. Tooling layer

### Context Enrichment Agent (MCP Tool)

- **Type**: Model Context Protocol (MCP) Service
- **Role**: A shared, high-speed Tool Node used by the other agents (primarily Behavior, Safety, and Orchestrator).
- **Action**: Translates coordinates and timestamps into rich contextual metadata (road type, legal speed limit, hotspot risk, weather).
- **Constraints**: Must return payloads in < 2 seconds. Fails over gracefully to default mappings to prevent blocking the graph.
