# Research & Findings: TraceData.ai

## Architectural Governance

- **Agent vs Monolith**: Our "Master Plan" defines 8 Agents. We must be careful not to rebuild the entire application inside the agents.
  - **Principle**: Agents handle _Reasoning_ (AI), Monolith handles _State & CRUD_ (Business Logic).
  - **Risk**: Agents calling each other directly without a clear protocol creates a "distributed monolith" nightmare.
  - **Mitigation**: Enforce the `AgentMessage` protocol rigidly in `common-lib`.

## Security & XAI

- **Simulated Data**: Ensure we inject tangible bias (e.g., younger drivers = higher risk) into the simulation now, so we can detect it with AIF360 later.
- **Explainability**: Every Agent output must have a `reasoning_trace` field for audit logging.
