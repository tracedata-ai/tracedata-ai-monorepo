# agents/driver_support

Dinesh's coaching agent for driver support. Runs as an independent Celery worker container.

- **agent.py**: `DriverSupportAgent` class inheriting from `TDAgentBase`.
- **graph.py**: Support-specific LangGraph nodes.
- **tools.py**: Coaching tip generation and notification tools.
- **tasks.py**: Celery task definition for `generate_coaching`.
