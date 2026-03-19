# TraceData Implementation Patterns

This module defines the project structure, component standards, and integration patterns for AI agents.

```
d:/learning-projects/tracedata-ai-monorepo/
├── frontend/                        # Next.js Application
└── backend/                       # Agentic AI Middleware
    ├── app/                         # CORE PACKAGE
    │   ├── core/                    # Engine & Config (DB)
    │   └── services/                # Business Logic
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
const { data, loading } = useAgentQuery("/api/agent-query");
```

## Real-Time Safety Alerts

Handled via direct triggers from the Telemetry Ingestion endpoint to the UI with <500ms latency.

---

## Homepage Component Patterns

The homepage (`page.tsx`) follows these patterns. Keep them consistent when adding new sections.

### `useInView` Hook — Scroll-triggered Animations

```tsx
function useInView(threshold = 0.18) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) { setVisible(true); observer.disconnect(); }
      },
      { threshold }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [threshold]);
  return { ref, visible };
}

// Usage — attach ref to the section element, toggle .is-visible on children
const { ref, visible } = useInView(0.1);
<section ref={ref as React.RefObject<HTMLElement>}>
  <div className={`fade-in-up ${visible ? "is-visible" : ""}`}>...</div>
</section>
```

> Use `observer.disconnect()` after first trigger — animations run **once**, not on every scroll.

### `useScrollProgress` Hook — Progress Bar

```tsx
function useScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const onScroll = () => {
      const el = document.documentElement;
      const total = el.scrollHeight - el.clientHeight;
      setProgress(total > 0 ? (el.scrollTop / total) * 100 : 0);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return progress;
}
```

### `homepageCopy` Data Shape Rules

All homepage text must live in the top-level `homepageCopy` const — **never inline strings in JSX**.

```tsx
// ✅ Correct — all cards are objects with { title, body }
const homepageCopy = {
  ecosystem: {
    cards: {
      safety:    { title: "...", body: "...", queue: "...", action: "..." },
      behavior:  { title: "...", body: "..." },
      coaching:  { title: "...", body: "..." }, // Tool Gateway cards also objects
    }
  }
}

// ❌ Wrong — mixing plain strings and objects breaks TypeScript type inference
coaching: "Tool Gateway: Context Enrichment",  // was a bug — fixed
```

### Section Anatomy

Every homepage section should:

1. Accept a `ref` from `useInView` on the `<section>` element
2. Have a **section `id`** matching a `navAnchors` / `footerAnchors` entry
3. Have a consistent **eyebrow → h2 → description** header structure
4. Use `fade-in-up` + `stagger-N` on cards/columns for entrance animation
5. Use `card-glow` on interactive cards

```tsx
function MySection() {
  const { ref, visible } = useInView();
  return (
    <section id="my-section" ref={ref as React.RefObject<HTMLElement>} className="...">
      <span className={`... ${monoFont.className}`}>eyebrow label</span>
      <h2 className={`... ${displayFont.className}`}>Section Title</h2>
      <p className="... text-[#bdc8d0]">Description text.</p>
      <div className={`card-glow fade-in-up stagger-1 ... ${visible ? "is-visible" : ""}`}>
        ...card content...
      </div>
    </section>
  );
}
```

### Nav & Footer Anchor Maps

All nav and footer links must route through lookup maps — never hardcode `href` on link elements directly:

```tsx
const navAnchors: Record<string, string> = {
  "7 Gaps": "#ecosystem",
  "Agent Scope": "#explainability",
  "Tech Stack": "#tech-specs",
  "Governance": "#integrity",
};
// footerAnchors follows the same pattern, keyed by group then label
```


---

## React Flow (Agent Dataflow) Patterns

The Agent Flow page uses `@xyflow/react` for pipeline visualization. Key files:

```
frontend/src/
├── components/agent-flow/
│   ├── flow-data.ts          # Node + Edge definitions (placeholder data)
│   ├── AgentNode.tsx         # Custom node component
│   └── AgentFlowCanvas.tsx   # ReactFlow canvas + simulation hook
└── app/fleet-manager/agent-flow/
    └── page.tsx              # Page shell (top bar, legend, controls)
```

### Data Shape (`flow-data.ts`)

```typescript
export type AgentStatus = "idle" | "running" | "success" | "warning" | "error";

export interface AgentNodeData {
  label: string;       // Display name
  subtitle: string;    // Role / tech note
  status: AgentStatus;
  elapsed?: string;    // e.g. "2.1s" or "—"
  type: "source" | "tool" | "agent" | "queue" | "output";
  [key: string]: unknown; // Required by @xyflow/react Node generic
}
```

> **Critical**: the `[key: string]: unknown` index signature is required for `@xyflow/react` compatibility.

### Custom Node Pattern (`AgentNode.tsx`)

```tsx
import { type NodeProps } from "@xyflow/react";

// Use bare NodeProps — do NOT use NodeProps<AgentNodeData>
function AgentNodeComponent(props: NodeProps) {
  const data = props.data as AgentNodeData; // cast inside body
  // ...
}
export const AgentNode = memo(AgentNodeComponent);
```

### Canvas Wrapper Pattern (`AgentFlowCanvas.tsx`)

```tsx
import { type NodeTypes } from "@xyflow/react";

// Cast to satisfy @xyflow/react internal generic constraint
const nodeTypes: NodeTypes = { agentNode: AgentNode as NodeTypes[string] };

// Simulation: setInterval on agent nodes when simulating=true
// Wire to real API: replace setInterval with polling or SSE
```

### Page Shell Pattern

```tsx
// Must be dynamic-imported with ssr:false — React Flow uses browser APIs
const AgentFlowCanvas = dynamic(
  () => import("@/components/agent-flow/AgentFlowCanvas").then((m) => m.AgentFlowCanvas),
  { ssr: false }
);

// key={resetKey} re-mounts the canvas for a full reset
<AgentFlowCanvas key={resetKey} simulating={simulating} />
```

### Connecting to Real Backend

When the backend agent status endpoint is ready:

1. Replace the `setInterval` simulation in `AgentFlowCanvas.tsx` with a `useEffect` that polls `/api/agents/status` every N seconds.
2. Map each API response field to the corresponding node's `status` and `elapsed` fields via `setNodes`.
3. Keep `simulating` as a fallback prop for offline/demo use.

```typescript
// Backend API shape to target:
// GET /api/agents/status → { agents: { id: string, status: AgentStatus, elapsed: string }[] }
```
