# core/ingestion

The telemetry ingestion pipeline. Runs as an independent worker container.

- **sidecar.py**: `IngestionSidecar` implementting the 7-step security and validation pipeline.
- **injection.py**: `InjectionScanner` for OWASP LLM01 mitigation.
- **transformer.py**: Transformer for `TelemetryPacket` → `TripEvent`.
- **worker.py**: Entry point for the ingestion worker process.
