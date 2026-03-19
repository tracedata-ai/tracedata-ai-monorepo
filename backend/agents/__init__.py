"""
TraceData Backend — Agents Package.

Contains the 5 AI agents co-located in this container:
  - orchestrator: Routes user requests to specialist agents
  - ingestion:    Parses and normalises incoming telemetry/trip data
  - behavior:     Scores driving behaviour with AIF360 bias correction
  - feedback:     Generates driver coaching feedback
  - safety:       Detects critical events and triggers maintenance alerts
"""
