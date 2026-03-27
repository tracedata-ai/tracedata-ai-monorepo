# security

Security boundary and PII protection. Shared module imported by all agents and the ingestion tool.

- **intent_gate.py**: The `@unified_tool_gateway` decorator for runtime intent verification.
- **capsule.py**: Logic for signing and verifying `IntentCapsule` (HMAC).
- **scoped_token.py**: Creation and validation of context-specific scoped tokens.
- **pii.py**: `PIIScrubber` for anonymising driver IDs and GPS rounding.
