# TraceData Implementation Patterns

This module defines the project structure, component standards, and integration patterns for AI agents.

```
d:/learning-projects/tracedata-ai-monorepo/
├── frontend/                        # Next.js Application
└── ai-agents/                       # Agentic AI Middleware
    ├── app/                         # CORE PACKAGE
    │   ├── core/                    # Engine & Config (Celery, DB)
    │   └── services/                # Logic (Kafka, Tasks)
    ├── scripts/                     # Tooling (Simulator, Seeding)
    ├── pyproject.toml               # uv Project Manifest
    ├── uv.lock                      # Generated Lockfile
    └── entrypoint.sh                # Container Orchestrator
```

## Dependency Management (uv)

TraceData uses **uv** for lightning-fast, reproducible builds.

1.  **Strict Locking**: Never run without `uv.lock`. This ensures every developer uses the exact same package version.
2.  **Explicit Scopes**: Use `uv add` to manage the `pyproject.toml`.
3.  **Container Optimization**: Our `Dockerfile` uses staged builds to pull the `uv` binary, ensuring zero-overhead installations.

## Database Seeding (Nuke & Pave)

To maintain a clean state during development, we use the **Nuke & Pave** pattern:

1.  **Idempotency**: Seeding scripts must check `if count == 0` for all tables.
2.  **RESET_DB Toggle**: Controlled via environment variable. 
    - `RESET_DB=true`: Drops the schema and re-seeds from `seed_data.json`.
    - `RESET_DB=false`: Skips seeding if data exists (Safe for prod).
3.  **External Data**: All mock data must reside in JSON files, never hardcoded in Python logic.

Every Python module in the `app/` package must follow the self-documenting pattern:

1. **Module Docstrings**: Clear explanation of the file's purpose at the top.
2. **Standard Docstrings**: All classes and functions must have Google-style docstrings (`Args`, `Returns`).
3. **Pydantic Field Metadata**: Use `Field(..., description="...")` for all API-facing schemas.

```python
# Example: app/schemas/telemetry.py
class Telemetry(BaseModel):
    """Schema for vehicle telemetry ingestion."""
    event_id: str = Field(..., description="UUID for the event")
```

## Component Anatomy

Every component should follow this structure:

```typescript
'use client';

import { FC, ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface Props {
  title: string;
  className?: string;
}

export const Component: FC<Props> = ({ title, className }) => {
  return (
    <div className={cn('p-4', className)}>
      <h2>{title}</h2>
    </div>
  );
};
```

## Key Principles

- Use `'use client'` explicitly for interactivity.
- Document all code with JSDoc-style technical comments.
- Use TypeScript strict mode; no `any`.
- Use `cn()` utility for Tailwind merging.

## Agent-Aware Components

Components interacting with agents must have clear boundaries.

```typescript
// Example: useAgentQuery for Orchestrator Agent
const { data, loading } = useAgentQuery('/api/agent-query');
```

## Real-Time Safety Alerts

Uses WebSocket to bridge Kafka events to the UI with <500ms latency.
