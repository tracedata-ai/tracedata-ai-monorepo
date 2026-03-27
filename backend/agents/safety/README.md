# agents/safety

Bala's agent for real-time safety analysis. Runs as an independent Celery worker container.

- **agent.py**: `SafetyAgent` class inheriting from `TDAgentBase`.
- **graph.py**: Safety-specific LangGraph nodes.
- **tools.py**: Safety-specific tools (collision analysis, road risk evaluation).
- **tasks.py**: Celery task definition for `analyse_event`.
