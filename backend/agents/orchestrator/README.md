# agents/orchestrator

The main task router and state machine. Runs as an independent worker container.

- **graph.py**: The LangGraph `StateGraph` definition for the Orchestrator logic.
- **nodes/**: Individual nodes for routing, cache warming, and agent dispatch.
- **db_manager.py**: Internal manager class for lock lifecycle and database state transitions.
- **health_monitor.py**: Background thread monitoring Redis health and buffer depths.
- **worker.py**: Entry point for the orchestrator worker process.
