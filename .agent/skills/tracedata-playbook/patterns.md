# TraceData Implementation Patterns

This module defines the project structure, component standards, and integration patterns for AI agents.

```
d:/learning-projects/tracedata-ai-monorepo/
├── frontend/                        # Next.js Application
└── ai-agents/                       # Agentic AI Middleware
    ├── app/                         # CORE PACKAGE
    │   ├── agents/                  # LangGraph workflows
    │   ├── api/                     # FastAPI Routers
    │   ├── models/                  # SQLAlchemy Entities
    │   ├── schemas/                 # Pydantic Schemas
    │   └── main.py                  # Service Entry
    ├── tests/                       # Pytest Smoke/Unit tests
    ├── Dockerfile                   # Container config
    └── requirements.txt             # Python deps
```

## Backend Anatomy

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
