# TraceData: Technical Requirements Specification

## SWE5008 Capstone Project - Requirements Document

---

## **1. Functional Requirements**

### **1.1 Telemetry Ingestion (FR-1)**

**Requirement:** System shall ingest sparse telematics payloads from 10,000+ truck devices.

**Specifications:**

- **Payload Format:** JSON (JSONB in PostgreSQL)
- **Required Fields:** trip_id, vehicle_id, timestamp
- **Optional Fields (Sparse):** speed, cabin_temp, atmosphere_temp, acceleration, harsh_brake, rpm, fuel_consumption, tire_pressure, steering_angle, throttle_position
- **Frequency:** 1 ping per minute per vehicle (10,000 trucks × 60 pings/hour)
- **Protocol:** HTTPS to Kafka or direct MQTT
- **Data Validation:**
  - Speed: 0-150 km/h
  - Cabin temp: -10 to 60°C
  - Atmosphere temp: -40 to 60°C
  - Timestamps: ISO 8601 format

**Acceptance Criteria:**

- ✅ Successfully ingest 10,000 concurrent telemetry streams
- ✅ Validate sparse payloads (no null rejection)
- ✅ 99.9% data persistence (no loss)
- ✅ < 1 second latency (Kafka → DB)

---

### **1.2 Trip Scoring with Fairness Audit (FR-2)**

**Requirement:** System shall score completed trips (0-100) using XGBoost with fairness bias correction.

**Specifications:**

- **Trigger:** End-of-trip event detected by Orchestrator
- **Model:** XGBoost (trained on historical trip data)
- **Features:** Speed, acceleration, harsh braking, cabin_temp, atmosphere_temp, road_type, hotspot_risk, trip_duration
- **Output:** Numeric score (0-100) + fairness_flag (boolean)
- **Fairness Metric:** Statistical Parity Difference (SPD)
  - Target: SPD < 0.5 (88% reduction from -6.9)
  - Cohorts: Novice (< 1yr) vs Expert (> 5yr)
  - Bias Correction: AIF360 Reweighting preprocessor
- **Explainability:**
  - LIME: Local explanation per trip (top 3 factors)
  - SHAP: Feature importance across driver cohort
  - Output: Feature importance JSON in decision log

**Acceptance Criteria:**

- ✅ Score generated < 3 seconds after trip end
- ✅ SPD measured monthly (report in decision_log)
- ✅ SPD drift detection (if SPD > 0.2, trigger retraining)
- ✅ LIME/SHAP explanations for 100% of scores
- ✅ No score variance > 5% across identical trips

---

### **1.3 Driver Appeals & Contestability (FR-3)**

**Requirement:** System shall accept driver appeals and process with full audit trail.

**Specifications:**

- **Appeal Types:** Fairness dispute, process complaint, emotional support request, safety concern
- **Input:** Driver submits via app (trip_id, appeal_text, optional emotion_rating 1-10)
- **Processing:**
  - Classify appeal type (deterministic rules or LLM)
  - Fetch original trip score + LIME explanation
  - Route to Advocacy Agent for response generation
  - Possible escalation to Fleet Manager if complex
- **Response Time:** < 24 hours
- **Logging:** All appeals logged in advocacy_appeals table with:
  - appeal_id, trip_id, driver_id, appeal_text, appeal_type, appeal_status, fm_decision, timestamp

**Acceptance Criteria:**

- ✅ 100% of appeals logged
- ✅ Audit trail queryable by driver_id or trip_id
- ✅ FM can review + override decision
- ✅ Driver notified of decision status
- ✅ No data loss (cascading deletes on driver deletion)

---

### **1.4 Emotional Trajectory & Burnout Detection (FR-4)**

**Requirement:** System shall track driver emotional state and detect burnout risk.

**Specifications:**

- **Trigger:** Driver submits feedback (optional emotion_rating 1-10)
- **Tracking Window:** Last 5 feedback events (rolling window)
- **Metrics:**
  - emotional_state: happy, neutral, stressed, very_stressed
  - risk_level: 0-1 (0=healthy, 1=burnout imminent)
  - trend_direction: improving, declining, stable
- **Burnout Threshold:** risk_level > 0.7
- **Alert:** If burnout detected, notify FM + Driver via app
- **Output:** sentiment_trends table with driver_id, emotional_state, risk_level, trend_direction, burnout_flag

**Acceptance Criteria:**

- ✅ Emotional state updated in real-time
- ✅ Burnout alerts sent < 5 minutes of detection
- ✅ False positive rate < 10% (manual validation needed)
- ✅ Historical trend visible in driver app

---

### **1.5 Personalized Coaching (FR-5)**

**Requirement:** System shall generate personalized coaching based on trip score + emotional state.

**Specifications:**

- **Trigger:** Behavior Agent flags coaching_needed OR Advocacy Agent requests support
- **Tone Selection:**
  - Encouraging (for healthy drivers, good performance)
  - Supportive (for stressed drivers)
  - Directive (for repeated violations)
  - Tone based on emotion_state from Sentiment Agent (if available)
- **Content:**
  - Focus areas (specific infractions to improve)
  - Encouragement (acknowledge strengths)
  - Actionable next steps (concrete improvements)
  - Personalized examples from driver's trip history
- **Delivery:** App notification + email
- **Optional LLM:** Can use LLM for tone/content generation (with fallback to rule-based coaching)

**Acceptance Criteria:**

- ✅ Coaching generated < 3 seconds after score
- ✅ Tone matches driver's emotional state (subjective evaluation)
- ✅ Focus areas match trip infractions (rule-based validation)
- ✅ Uniqueness: No two drivers get identical coaching (personalization check)

---

### **1.6 Private Feedback & Driver Listening (FR-6)**

**Requirement:** System shall accept private feedback from drivers with strict privacy controls.

**Specifications:**

- **Input:** Driver app form (free-text, optional emotion_rating)
- **Privacy Guarantees:**
  - Feedback stored in driver_input table
  - NOT accessible to Fleet Manager (separation of concerns)
  - Only accessible to: Driver (own data), Sentiment/Advocacy agents, Compliance audit (with notice)
  - Cannot be used for scoring/penalization
- **Storage:** Encrypted at rest (PostgreSQL encryption)
- **PDPA Compliance:**
  - Right to access (driver can request their feedback)
  - Right to deletion (feedback deleted on driver request)
  - Audit logging (track who accessed feedback)

**Acceptance Criteria:**

- ✅ FM cannot view driver_input via API
- ✅ Query access logging (audit trail)
- ✅ Encryption verified (manual security review)
- ✅ PDPA deletion tested (cascade + restore verification)

---

### **1.7 Critical Incident Handling (FR-7)**

**Requirement:** System shall detect + escalate critical safety incidents in real-time.

**Specifications:**

- **Incidents:** Collision, hard brake (>0.6g), engine malfunction, loss of signal
- **Detection:** From telemetry Critical priority stream
- **Processing:**
  - Immediate (realtime path, not async)
  - Escalate to Fleet Manager within 30 seconds
  - Include context (location, vehicle state, driver info)
  - Optional: Notify driver (optional feature)
- **Escalation:** Alert + dashboard update + email to FM
- **Logging:** safety_incidents table with incident_id, incident_type, severity, timestamp, fm_notified, fm_action

**Acceptance Criteria:**

- ✅ Incident detection latency < 5 seconds
- ✅ FM notification latency < 30 seconds
- ✅ 100% incident logging (no data loss)
- ✅ Can query incidents by vehicle_id or driver_id
- ✅ FM can mark as resolved/investigating

---

### **1.8 Context Enrichment (FR-8)**

**Requirement:** System shall enrich trips with contextual data (road, speed, weather).

**Specifications:**

- **Trigger:** Synchronous calls from Behavior, Advocacy, Coaching, Sentiment, Safety agents
- **Lookups:**
  - Road type (highway, urban, rural) via map matching (GPS → segment)
  - Speed limit (from road database, e.g., OpenStreetMap)
  - Hotspot risk (historical incident frequency in region)
  - Weather (optional, from API)
- **Response Time:** < 100ms (critical for blocking task execution)
- **Fallback:** If lookup fails, use cached default values (last known good)
- **Output:** context_enrichment table with trip_id, road_type, speed_limit, hotspot_risk, weather

**Acceptance Criteria:**

- ✅ Context latency < 100ms (p99)
- ✅ Accuracy: Road type matches actual road (manual validation, 100 samples)
- ✅ Speed limit accuracy: ±5 km/h (vs actual posted limits)
- ✅ Fallback works (no task failures if lookup down)

---

## **2. Non-Functional Requirements**

### **2.1 Performance (NFR-1)**

**Requirement:** System shall meet latency and throughput targets.

| Metric                         | Target              | Acceptable Range |
| ------------------------------ | ------------------- | ---------------- |
| Telemetry ingestion → DB       | < 1 sec             | 0.5 - 2 sec      |
| End-of-trip detection          | < 5 sec             | 2 - 10 sec       |
| Trip scoring (Behavior Agent)  | < 3 sec             | 1 - 5 sec        |
| Feedback classification (LLM)  | < 2 sec             | 1 - 5 sec        |
| Context lookup (sync)          | < 100ms             | 50 - 200ms       |
| Full trip-to-coaching pipeline | < 10 sec            | 5 - 15 sec       |
| **Throughput**                 | 10,000 vehicles/min | ≥ 8,000/min      |
| **API Response (REST)**        | < 500ms             | < 1 sec          |

**Testing:**

- Load test with 10,000 concurrent telemetry streams
- Profile bottlenecks (Kafka, DB, agent execution)
- Horizontal scaling (auto-scale Celery workers)

---

### **2.2 Reliability & Availability (NFR-2)**

**Requirement:** System shall achieve 99.9% uptime (43.2 min downtime/month allowed).

**Specifications:**

- **Kafka:** Multi-broker cluster (3 brokers minimum)
- **Database:** Multi-AZ RDS with automated failover
- **API:** Auto-scaling (2-4 instances behind ALB)
- **Workers:** Auto-scaling Celery (4-8 workers)
- **Backup:** Daily snapshots, 30-day retention
- **Disaster Recovery:** RTO < 1 hour, RPO < 5 minutes

**Acceptance Criteria:**

- ✅ 99.9% uptime verified over 30 days
- ✅ No data loss during failover
- ✅ Graceful degradation (non-critical features optional)
- ✅ Retry logic (Celery exponential backoff)

---

### **2.3 Data Integrity (NFR-3)**

**Requirement:** System shall guarantee data integrity for all persistent stores.

**Specifications:**

- **Constraints:**
  - Foreign key integrity (appeals → trips)
  - No orphaned records (cascade delete on driver removal)
  - Unique constraints (trip_id, appeal_id, sentiment_log_id)
- **Transactional Consistency:** ACID for all writes
- **Idempotency:** Duplicate Kafka messages → single DB record (event_id deduplication)
- **Validation:**
  - Schema validation (JSON schema for sparse payloads)
  - Referential integrity checks
  - Data range validation (e.g., score 0-100)

**Acceptance Criteria:**

- ✅ No constraint violations in test suite
- ✅ Duplicate message handling verified
- ✅ Data consistency after failures (restore test)
- ✅ ACID compliance verified (transaction logs)

---

### **2.4 Scalability (NFR-4)**

**Requirement:** System shall scale horizontally to support growth.

**Specifications:**

- **Horizontal Scaling:**
  - FastAPI: Add instances behind ALB (auto-scale based on CPU)
  - Celery: Add workers for agent execution (queue-depth based)
  - Kafka: Add brokers if throughput > 100k msgs/min
  - PostgreSQL: Read replicas for query offloading
- **Vertical Scaling:**
  - RDS instance type upgradeable (db.r5.xlarge → db.r6i.2xlarge)
  - Redis upgradeable (m5.large → r6g.xlarge)
- **Future Growth:** Designed for 50,000 vehicles (5x current scope)

**Testing:**

- Stress test to 50,000 vehicles
- Measure resource utilization (CPU, memory, disk I/O)
- Identify scaling bottlenecks

---

### **2.5 Security (NFR-5)**

**Requirement:** System shall protect sensitive driver data and comply with PDPA.

**Specifications:**

- **Encryption:**
  - TLS 1.2+ for all network communication
  - AES-256 for data at rest (PostgreSQL)
  - Secrets stored in AWS Secrets Manager (API keys, DB passwords)
- **Authentication:** JWT tokens (FastAPI) with 1-hour expiry
- **Authorization:**
  - Role-based access control (Driver, Fleet Manager, Admin)
  - Driver can only access own data
  - FM cannot access driver_input (private feedback)
- **Audit Logging:**
  - All data access logged (who, what, when)
  - Especially sensitive: appeals, feedback, fairness flags
- **PDPA Compliance:**
  - Data retention: 2 years (configurable)
  - Right to access: API endpoint to download all driver data
  - Right to deletion: Cascade delete with audit trail
  - Purpose limitation: Data used only for stated purposes

**Testing:**

- Penetration testing (manual security review)
- PDPA compliance checklist (access control, audit logging)
- Encryption verification (manual inspection)

---

### **2.6 Maintainability (NFR-6)**

**Requirement:** System code shall be well-structured, documented, and testable.

**Specifications:**

- **Code Quality:**
  - Test coverage ≥ 80%
  - Pylint/Black formatting
  - Type hints for all functions
  - Docstrings for all modules/classes/functions
- **Documentation:**
  - README (setup, deployment, testing)
  - Architecture doc (this file + system design)
  - API documentation (OpenAPI/Swagger)
  - Agent documentation (inputs, outputs, decision logic)
- **Modularity:**
  - Each agent in separate file/module
  - Agents import from shared utilities (DB, logging)
  - No circular dependencies
- **Versioning:** Git with semantic versioning (v1.0.0, etc.)

**Testing:**

- Linting passes (Pylint score > 8.5/10)
- Coverage report generated per commit
- Documentation auto-generated from docstrings

---

## **3. Technical Constraints**

### **3.1 Technology Stack**

**Mandatory:**

- Backend: Python 3.9+ (FastAPI)
- Orchestration: LangGraph
- ML/XAI: XGBoost, AIF360, SHAP, LIME
- Streaming: Apache Kafka
- Database: PostgreSQL 12+ with JSONB
- Task Queue: Celery + Redis

**Optional:**

- LLM: OpenAI API or local LLM (fallback to rules if unavailable)
- Frontend: Next.js (user-facing)

**NOT Allowed:**

- Microservices (monolith simpler for capstone scope)
- Polyglot (Python-only backend for simplicity)
- NoSQL only (PostgreSQL required for ACID)

---

### **3.2 Data Constraints**

**Sparse Telemetry:**

- No full payloads (only non-null values)
- Compression via JSONB (PostgreSQL handles)
- Storage: 7.2 GB/month (for 10,000 trucks at 1 ping/min)

**Data Retention:**

- Raw telemetry: 90 days (then archive to S3)
- Trip scores: 2 years
- Appeals: 5 years (legal requirement)
- Decision log: 2 years

**Privacy:**

- driver_input encrypted at rest
- No driver_input accessible to FM API
- PII minimal (driver_id only, no name/email stored)

---

### **3.3 Operational Constraints**

**Deployment:**

- AWS only (EC2, RDS, MSK, S3, ALB)
- Single region (Singapore: ap-southeast-1)
- Infrastructure as Code (Terraform, not manual setup)

**Monitoring:**

- CloudWatch metrics (latency, errors, throughput)
- Alerts for SLO breaches (latency > 5 sec, error rate > 1%)
- Dashboard with real-time system health

---

## **4. Test Requirements**

### **4.1 Test Coverage**

| Category                 | Count  | Coverage                             |
| ------------------------ | ------ | ------------------------------------ |
| Unit tests               | 30     | 80% of code                          |
| Integration tests        | 12     | Happy path + error cases             |
| Fairness tests           | 6      | Bias injection + mitigation          |
| LLM resilience tests     | 5      | Fallback, timeouts, hallucination    |
| Privacy/Compliance tests | 3      | PDPA, access control                 |
| Load tests               | 2      | 10K concurrent, sustained throughput |
| **Total**                | **58** | **Comprehensive**                    |

### **4.2 Fairness Testing**

**Test Cases:**

1. Inject bias: Give novice drivers harder trips (night, urban)
2. Verify detection: SPD calculation shows -6.9 bias
3. Apply mitigation: AIF360 reweighting applied
4. Verify correction: SPD improves to -0.8
5. Validate performance: ROC-AUC maintained at 0.78
6. Monitor drift: Monthly SPD audit, retrain if drift > 0.2

**Manual Validation:**

- 100 sample trips reviewed by domain expert
- Fairness judgment: "Is this score fair?" (subjective)
- Bias mitigation effectiveness: "Is the system less biased?"

---

## **5. Acceptance Criteria Checklist**

### **Architecture**

- [ ] 8 agents implemented (Ingestion Quality, Orchestrator, Behavior, Advocacy, Sentiment, Coaching, Safety, Context)
- [ ] Kafka streaming (2 topics: telemetry, high-priority)
- [ ] Async execution (Celery) except Context Enrichment (sync)
- [ ] Sparse telemetry payloads (only non-null values)
- [ ] Agent output tables (9 total + decision_log)
- [ ] Junction merging (all agent flows converge)

### **Fairness**

- [ ] Fairness metric: SPD < 0.5 (88% improvement from -6.9)
- [ ] LIME/SHAP explanations for 100% of scores
- [ ] AIF360 bias correction in Behavior Agent
- [ ] Fairness test suite (6 tests, all passing)
- [ ] Monthly fairness audit (SPD monitoring)

### **Data & Privacy**

- [ ] PDPA compliance verified (access control, deletion)
- [ ] Private feedback inaccessible to FM
- [ ] Audit logging (all data access)
- [ ] Data integrity tests (constraints, idempotency)
- [ ] Encryption at rest (PostgreSQL) + in transit (TLS)

### **Testing**

- [ ] 58 tests passing (30 unit + 12 integration + 6 fairness + 5 LLM + 3 privacy + 2 load)
- [ ] 80%+ code coverage
- [ ] Load test: 10,000 concurrent streams
- [ ] Latency targets met (all SLAs < target)

### **Documentation**

- [ ] Architecture doc complete (this file)
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Agent documentation (inputs, outputs, logic)
- [ ] Deployment guide (setup, scaling)
- [ ] Code comments & docstrings

### **Demonstration**

- [ ] Working prototype (device → score → coaching pipeline)
- [ ] Sample data + pilot results
- [ ] Fairness case study (before/after SPD)
- [ ] Presentation slides (20-25 slides)

---

## **6. Change Log**

| Version | Date        | Changes                                                        |
| ------- | ----------- | -------------------------------------------------------------- |
| 0.1     | Mar 9, 2025 | Initial draft                                                  |
| 0.2     | Mar 9, 2025 | Added sparse payloads, hybrid Orchestrator, temperature fields |
| 1.0     | Mar 9, 2025 | Final version, all requirements locked                         |

---

**Document Version:** 1.0  
**Status:** Final - Ready for Development  
**Approval:** SWE5008 Capstone Team
