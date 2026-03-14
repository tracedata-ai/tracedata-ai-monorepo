# TraceData Domain-Driven Design (DDD)

This document details the strategic and tactical DDD patterns applied to the TraceData system, ensuring clear boundaries, robust aggregates, and scalable event-driven choreography.

## Strategic Design: Context Map

The TraceData system is divided into four primary Bounded Contexts, coordinated via an asynchronous event bus and managed by a deterministic orchestrator.

### Context Map Diagram

```mermaid
graph TB
    subgraph External["External Environment"]
        IoT[Vehicle IoT Telemetry]
        App[Driver App / Feedback]
    end

    subgraph TelemetryContext["Telemetry & Safety Context"]
        ACL[Data Cleaner Gateway<br/><< ACL >>]
        Safety[Safety Agent<br/><< Command / Fast Path >>]
        Agg1[(Trip & Incident Aggregates)]
        
        ACL --> Safety
        Safety --> Agg1
    end

    subgraph EventBus["Event Bus (Redis/Celery)"]
        E1((TripEnded))
        E2((IncidentDetected))
        E3((TripScored))
        E4((FeedbackSubmitted))
    end

    subgraph EvaluationContext["Driver Evaluation Context"]
        Behavior[Behavior Evaluation Agent<br/><< ML / XGBoost >>]
        Agg2[(TripScore Aggregate)]
    end

    subgraph WellnessContext["Driver Wellness Context"]
        Wellness[Driver Wellness Analyst<br/><< GenAI / NLP >>]
        Agg3[(DriverProfile & Appeal Aggregates)]
    end

    subgraph OrchestrationContext["Orchestration Context"]
        Orch[Deterministic Orchestrator<br/><< Saga Manager >>]
    end

    IoT --> ACL
    App --> ACL
    
    ACL -- Publishes --> E1
    ACL -- Publishes --> E4
    Safety -- Publishes --> E2
    Behavior -- Publishes --> E3
    
    E1 -. Subscribes .-> Behavior
    E3 -. Subscribes .-> Wellness
    E4 -. Subscribes .-> Wellness
    E2 -. Subscribes .-> Orch
```

### Strategic Patterns Applied

1.  **Bounded Contexts**:
    - **Telemetry & Safety**: Real-time ingestion and critical alerting.
    - **Driver Evaluation**: ML fairness and predictive scoring.
    - **Driver Support & Wellness**: Generative AI/NLP for coaching and appeals.
2.  **Anti-Corruption Layer (ACL)**: The **Data Cleaner Gateway** sanitizes external input before it reaches the core domain.
3.  **Domain Events (Choreography)**: Decoupled communication via `TripEnded`, `TripScored`, etc.
4.  **Saga Management**: The **Deterministic Orchestrator** manages complex, multi-step workflows (e.g., severe safety escalations) using compensations where necessary.

---

## Tactical Design: Domain Schema

Tactical DDD focuses on the internal structure of each context, defining the lifecycle of data through Aggregates, Entities, and Value Objects.

### Tactical Schema Diagram

```mermaid
classDiagram
    namespace TelemetryAndSafety {
        class Trip {
            <<Aggregate Root>>
            +tripId string
            +driverId string
            +startOfTrip DateTime
            +endOfTrip DateTime
            +startTrip()
            +endTrip()
        }
        class TelemetryEvent {
            <<Entity>>
            +eventId string
            +category string
            +timestamp DateTime
            +validatePayload()
        }
        class RawTelemetry {
            <<Value Object>>
            +gpsLatitude float
            +gpsLongitude float
            +speed float
            +rpm float
        }
        class EnrichedContext {
            <<Value Object>>
            +weatherConditions string
            +roadType string
            +hazardWarnings string
        }
    }

    Trip "1" *-- "*" TelemetryEvent
    TelemetryEvent "1" *-- "1" RawTelemetry
    TelemetryEvent "1" *-- "1" EnrichedContext

    namespace DriverEvaluation {
        class TripScore {
            <<Aggregate Root>>
            +scoreId string
            +tripId string
            +safetyScore float
            +calculateScore()
        }
        class ExplainabilityContext {
            <<Value Object>>
            +shapValues Map
            +limeExplanations Map
        }
        class FairnessMetrics {
            <<Value Object>>
            +spdValue float
            +applyAIF360Reweighting()
        }
    }

    TripScore "1" *-- "1" ExplainabilityContext
    TripScore "1" *-- "1" FairnessMetrics

    namespace DriverWellness {
        class DriverProfile {
            <<Aggregate Root>>
            +driverId string
            +burnoutRiskLevel float
            +updateSentiment()
        }
        class Appeal {
            <<Entity>>
            +appealId string
            +rawUserInput string
            +sanitizedInput string
            +status string
            +processDispute()
        }
        class CoachingSession {
            <<Entity>>
            +coachingId string
            +emotionalTone string
            +actionablePoints string
            +generatePersonalizedCoaching()
        }
    }

    DriverProfile "1" *-- "*" Appeal
    DriverProfile "1" *-- "*" CoachingSession
```

### Tactical Patterns Applied

1.  **Aggregate Roots**:
    - `Trip`: Controls the telemetry lifecycle.
    - `TripScore`: Separates heavy ML scoring from ingestion to prevent database lock contention.
    - `DriverProfile`: Central hub for historical driver state and sentiment.
2.  **Entities**: Objects with identity and state transitions (e.g., `Appeal`, `TelemetryEvent`).
3.  **Value Objects**: Immutable attributes attached to entities (e.g., `RawTelemetry`, `FairnessMetrics`).
