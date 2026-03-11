# TraceData: Software Requirements Specification (SRS)
## SWE5008 Capstone Project

---

## **1. Introduction**

### **1.1 Purpose**
This document specifies the software requirements for TraceData, an AI-powered vehicle telematics and driver advocacy platform. It defines the functional and non-functional requirements, technical constraints, and acceptance criteria for the SWE5008 Capstone Project.

### **1.2 Scope**
TraceData ingests, processes, and analyzes vehicle telemetry data from 10,000+ commercial trucks. Unlike traditional penalizing telemetry systems, TraceData utilizes a Multi-Agent AI architecture to provide equitable trip scoring, fairness auditing, burnout detection, and personalized driver coaching.

---

## **2. Overall Description**

### **2.1 Product Perspective**
TraceData is an academic capstone project focusing primarily on advanced AI orchestration rather than a full-scale fleet management backend. The system is built as an **Agentic AI Middleware Monolith** (Python, FastAPI, LangGraph) providing specialized analytical and generative capabilities, serving a **Next.js** frontend application. While basic fleet components exist, they are nominal and scoped only to support the AI workflows.

### **2.2 User Classes and Characteristics**
1.  **Drivers:** End-users generating telemetry. They interact with the system via a mobile application to view scores, receive coaching, and submit private feedback or appeals.
2.  **Fleet Managers (FM):** Administrative users who monitor fleet safety, review escalated incidents, and manage overall operations.
3.  **System Administrators:** Technical users responsible for system health, fairness audits, and AI model governance.

### **2.3 Operating Environment**
-   **Infrastructure:** AWS (Single Region: ap-southeast-1).
-   **Hardware Interfaces:** Telematics IoT devices installed in 10,000+ trucks sending JSON over HTTPS/MQTT.

---

## **3. System Features (Functional Requirements)**

### **3.1 Telemetry Ingestion & Lifecycle Management (FR-1)**
**Requirement:** The system SHALL reliably ingest and process stateful vehicle telemetry data representing the trip lifecycle.

*   **Input Streams:**
    *   **Start-of-Trip Ping:** Marks trip boundary initiation, driver confirmation, and vehicle readiness.
    *   **4-Minute Batch Ping:** Regular heartbeat containing sparse event arrays and safe operation checkpoints.
    *   **End-of-Trip Ping:** Marks trip completion, encapsulates the full summary, and triggers backend ML scoring.
    *   **Emergency Ping:** Out-of-band transmission for critical events (e.g., collisions, panic button) requiring immediate response.
*   **Data Integrity:** The system SHALL ingest telemetry via **Apache Kafka** streams, organized by ping type, to ensure durability, high-throughput handling, and full event replayability. All payloads SHALL be persisted using Time-Series optimized storage, handling out-of-order or duplicate messages idempotently.
*   **State Management:** The system SHALL actively track "Active Trips" and handle "Zombie Trips" (missing End-of-Trip pings). Internal asynchronous task queuing and state management SHALL be orchestrated using **Redis** and **Celery**.

### **3.2 Trip Scoring & Fairness Audit (FR-2)**
**Requirement:** The system SHALL calculate a safety score (0-100) for completed trips using an XGBoost model, subject to automated fairness bias correction.

*   **Trigger:** Successful processing of the `End-of-Trip Ping` or a timeout-triggered synthetic trip closure.
*   **Fairness Metric:** Statistical Parity Difference (SPD) SHALL be maintained below 0.5 (comparing predefined cohorts such as Novice vs. Expert drivers).
*   **Explainability:** The system SHALL generate feature importance logs (via SHAP/LIME) for 100% of generated scores to facilitate transparency.

### **3.3 Driver Appeals & Contestability (FR-3)**
**Requirement:** The system SHALL provide a structured mechanism for drivers to dispute scores or raise safety/process concerns.

*   **Processing:** Appeals SHALL be classified and routed to an AI Advocacy Agent for initial response generation, with automatic escalation to Fleet Managers for complex or high-severity cases.
*   **Auditability:** A complete, tamper-evident audit trail of the appeal, AI reasoning, and final resolution SHALL be maintained.

### **3.4 Emotional Trajectory & Burnout Detection (FR-4)**
**Requirement:** The system SHALL calculate and monitor driver emotional states over time to preemptively detect burnout risk.

*   **Mechanism:** Analyzes the last 5 feedback events submitted by the driver (rolling window).
*   **Action:** If the computed `risk_level` exceeds the burnout threshold (0.7), the system SHALL immediately alert the Fleet Manager and trigger supportive workflows.

### **3.5 Personalized Coaching (FR-5)**
**Requirement:** The system SHALL dynamically generate actionable, personalized coaching recommendations.

*   **Content Generation:** Coaching tone (Encouraging, Supportive, Directive) SHALL be adapted based on the driver's current emotional state and specific trip infractions.
*   **Uniqueness:** No two coaching outputs for different drivers with different histories SHALL be identical.

### **3.6 Private Feedback & Driver Listening (FR-6)**
**Requirement:** The system SHALL allow drivers to submit private feedback that is cryptographically isolated from Fleet Manager visibility.

*   **Privacy Guarantees:** Feedback SHALL NOT be accessible via Fleet Manager APIs and SHALL NOT be used negatively in scoring models.
*   **PDPA Compliance:** The system SHALL support right-to-access and right-to-deletion requests for all submitted feedback.

### **3.7 Critical Incident Handling (FR-7)**
**Requirement:** The system SHALL process `Emergency Pings` strictly in real-time.

*   **SLA:** Critical incidents (e.g., collision detection) SHALL trigger Fleet Manager escalation mechanisms (dashboard alert, SMS/Email) within 30 seconds of ingestion.

### **3.8 Context Enrichment (FR-8)**
**Requirement:** The system SHALL enrich raw telemetry with geospatial and environmental context (road type, speed limits, weather risk).

*   **Performance:** Context lookups SHALL return within 100ms. If external APIs time out, the system SHALL seamlessly fallback to cached or default values without blocking downstream processing.

---

## **4. Non-Functional Requirements**

### **4.1 Performance & Scalability (NFR-1)**
*   **Throughput:** The system SHALL comfortably ingest batches from 10,000 concurrent vehicles without backpressure exhaustion.
*   **Latency:** Critical ML scoring (FR-2) SHALL complete in < 3 seconds; standard API responses SHALL be < 500ms.
*   **Scalability:** The architecture SHALL scale horizontally (compute, Kafka brokers, Redis clusters, and read-replicas) to accommodate 50,000 vehicles.

### **4.2 Reliability & Availability (NFR-2)**
*   **Uptime:** The system SHALL maintain 99.9% availability.
*   **Resilience:** The AI Multi-Agent workflows SHALL incorporate fallback mechanisms (e.g., reverting to deterministic rules if the LLM provider fails).

### **4.3 Security & Compliance (NFR-3)**
*   **Encryption:** All data SHALL be encrypted in transit (TLS 1.2+) and at rest (AES-256).
*   **Access Control:** Strict Role-Based Access Control (RBAC) SHALL be enforced. Drivers can only access their own data.
*   **Regulation:** Must comply fully with Singapore's Personal Data Protection Act (PDPA).

---

## **5. Technical & Domain Constraints**

*   **Architecture Pattern:** Agentic AI Middleware Monolith (Python) + Next.js Frontend. As an academic project, the scope is deliberately constrained to exclude a full-featured traditional fleet management backend.
*   **Stream Ingestion:** Apache Kafka SHALL be used for all external telemetry ingestion to mirror industry standards and provide event replayability across different topic pipes.
*   **Internal Queueing & State:** Redis and Celery SHALL be used for all asynchronous task queueing, state management (e.g., tracking active vs. zombie trips), and background processing within the AI middleware.
*   **Data Storage:** A single organizational PostgreSQL database SHALL be used. While schemas for fleet data (e.g., vehicles, drivers) will exist, they are nominal and designed strictly to provide the necessary state and context for the AI agents.
*   **AI Agents:** LangGraph SHALL be used for orchestrating cyclical agent workflows (e.g., Context loops, Refinement).

---

## **6. Acceptance & Testing Requirements**

1.  **Unit & Integration:** ≥ 80% code coverage across core monolithic modules and Python agents.
2.  **Fairness Validation:** SPD calculations must provably shift from a baseline bias (e.g., -6.9) to a neutral band (< 0.5) using AIF360/Reweighting.
3.  **Privacy Audit:** Verification that `driver_input` tables are inaccessible to Fleet Management DB roles and APIs.
4.  **Load Testing:** Sustained throughput simulation representing 10,000 active trucks operating the 4-ping lifecycle over a 24-hour period.

---
**Document Version:** 1.1 (Updated to Industry SRS Standard)
**Status:** Approved for Architectural Review
