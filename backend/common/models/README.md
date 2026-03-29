# common/models

This directory contains all Pydantic models used across the TraceData system.

- **events.py**: Definitions for `TelemetryPacket`, `TripEvent`, and `CompletionEvent`.
- **trips.py**: Definitions for `TripContext` and `TripStatus`.
- **scoring.py**: Definitions for `ScoringResult`, `SHAPValues`, and `FairnessResult`.
- **coaching.py**: Definitions for `CoachingResult` and `CoachingTip`.
- **security.py**: Definitions for `IntentCapsule`, `ScopedToken`, and `ExecutionContext`.
- **emergency.py**: Definitions for `EmergencyDispatchResult`.
