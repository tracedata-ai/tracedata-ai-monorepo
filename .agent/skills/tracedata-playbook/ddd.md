# TraceData Domain-Driven Design (DDD)

This document details the strategic and tactical DDD patterns applied to the TraceData system, ensuring clear boundaries, robust aggregates, and scalable event-driven choreography.

## Strategic Design: Context Map

The TraceData system is divided into four primary Bounded Contexts, coordinated via an asynchronous event bus and managed by a deterministic orchestrator.

### Context Map Diagram

```plantuml
@startuml
skinparam componentStyle rectangle

package "External Environment" {
    [Vehicle IoT Telemetry] as IoT
    [Driver App / Feedback] as App
}

package "Telemetry & Safety Context" {
    [Data Cleaner Gateway] <<Anti-Corruption Layer>> as ACL
    [Safety Agent] <<Command / Fast Path>> as Safety
    database "Trip & Incident Aggregates" as Agg1
}

package "Event Bus (Redis/Celery)" {
    () "TripEnded" as E1
    () "IncidentDetected" as E2
    () "TripScored" as E3
    () "FeedbackSubmitted" as E4
}

package "Driver Evaluation Context" {
    [Behavior Evaluation Agent] <<ML / XGBoost>> as Behavior
    database "TripScore Aggregate" as Agg2
}

package "Driver Wellness Context" {
    [Driver Wellness Analyst] <<Generative AI / NLP>> as Wellness
    database "DriverProfile & Appeal Aggregates" as Agg3
}

package "Orchestration Context" {
    [Deterministic Orchestrator] <<Saga Manager>> as Orch
}

IoT --> ACL : Raw Data
App --> ACL : Raw Text

ACL --> Safety
Safety --> Agg1

ACL ..> E1 : Publishes
ACL ..> E4 : Publishes
Safety ..> E2 : Publishes
Behavior ..> E3 : Publishes

E1 ..> Behavior : Subscribes
E3 ..> Wellness : Subscribes
E4 ..> Wellness : Subscribes
E2 ..> Orch : Subscribes

Orch ..> E1 : Coordinates Saga
Orch ..> E2 : Coordinates Saga
@enduml
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

```plantuml
@startuml
package "Telemetry & Safety Context" <<Rectangle>> {
    class Trip <<Aggregate Root>> {
        +String tripId
        +String driverId
        +DateTime startOfTrip
        +DateTime endOfTrip
        +startTrip()
        +endTrip()
    }
    
    class TelemetryEvent <<Entity>> {
        +String eventId
        +String category
        +DateTime timestamp
        +validatePayload()
    }
    
    class RawTelemetry <<Value Object>> {
        +Float gpsLatitude
        +Float gpsLongitude
        +Float speed
        +Float rpm
    }
    
    class EnrichedContext <<Value Object>> {
        +String weatherConditions
        +String roadType
        +String hazardWarnings
    }
    
    Trip "1" *-- "*" TelemetryEvent
    TelemetryEvent "1" *-- "1" RawTelemetry
    TelemetryEvent "1" *-- "1" EnrichedContext
}

package "Driver Evaluation Context" <<Rectangle>> {
    class TripScore <<Aggregate Root>> {
        +String scoreId
        +String tripId
        +Float safetyScore
        +calculateScore()
    }
    
    class ExplainabilityContext <<Value Object>> {
        +Map shapValues
        +Map limeExplanations
    }
    
    class FairnessMetrics <<Value Object>> {
        +Float spdValue
        +applyAIF360Reweighting()
    }
    
    TripScore "1" *-- "1" ExplainabilityContext
    TripScore "1" *-- "1" FairnessMetrics
}

package "Driver Wellness Context" <<Rectangle>> {
    class DriverProfile <<Aggregate Root>> {
        +String driverId
        +Float burnoutRiskLevel
        +updateSentiment()
    }
    
    class Appeal <<Entity>> {
        +String appealId
        +String rawUserInput
        +String sanitizedInput
        +String status
        +processDispute()
    }
    
    class CoachingSession <<Entity>> {
        +String coachingId
        +String emotionalTone
        +String actionablePoints
        +generatePersonalizedCoaching()
    }
    
    DriverProfile "1" *-- "*" Appeal
    DriverProfile "1" *-- "*" CoachingSession
}
@enduml
```

### Tactical Patterns Applied

1.  **Aggregate Roots**:
    - `Trip`: Controls the telemetry lifecycle.
    - `TripScore`: Separates heavy ML scoring from ingestion to prevent database lock contention.
    - `DriverProfile`: Central hub for historical driver state and sentiment.
2.  **Entities**: Objects with identity and state transitions (e.g., `Appeal`, `TelemetryEvent`).
3.  **Value Objects**: Immutable attributes attached to entities (e.g., `RawTelemetry`, `FairnessMetrics`).
