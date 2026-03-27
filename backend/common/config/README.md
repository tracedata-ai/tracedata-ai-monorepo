# common/config

This directory contains application configuration and constants.

- **settings.py**: Uses `pydantic-settings` to read configuration from environment variables and `.env`.
- **event_matrix.py**: Authority for `EVENT_MATRIX`, `PRIORITY_MAP`, and event-to-agent routing rules.
- **sla.py**: Definition of service level agreements like `PROCESSING_SLA`, `ACTION_SLA`, and `CONTEXT_TTL`.
