# TraceData Implementation Patterns

This module defines the project structure, component standards, and integration patterns for AI agents.

## Project Structure

```
src/
├── components/
│   ├── agents/                      # Agent-aware components
│   ├── explainability/              # XRAI rubric components
│   ├── security/                    # Cybersecurity rubric components
│   ├── shared/                      # Reusable templates & UI elements
│   └── fleet-operator/              # Domain-specific UI
├── pages/
│   ├── api/                         # Backend proxies & agent endpoints
│   └── fleet-operator/              # Page routes
├── lib/
│   ├── agent-client.ts              # Agent communication
│   ├── hooks/                       # SWR & WebSocket hooks
│   └── utils/                       # Security & A11y helpers
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
