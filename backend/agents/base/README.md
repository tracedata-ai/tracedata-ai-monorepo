# agents/base

Shared base class and decorators for all LLM-powered agents.

- **agent.py**: `TDAgentBase` class providing LangGraph lifecycle methods and common initialization.
- **decorators.py**: Security and logging decorators (`@validate_intent_capsule`, `@sanitise_input`, etc.).
