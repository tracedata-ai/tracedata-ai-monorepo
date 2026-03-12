---
name: tracedata-frontend
description: Complete frontend skill for TraceData capstone—enforces architecture (Python FastAPI + LangGraph middleware, Next.js frontend, multi-tenancy), design system (glassmorphism, Tailwind + Shadcn), and implementation patterns (XRAI, security, performance, accessibility). Aligns with all four rubric areas and integrates with Orchestrator Agent, Safety Agent, and telematics pipelines. Use for ALL frontend development, scaffolding, and UI/UX work.
---

# TraceData Frontend Playbook

This is the **single authoritative reference** for all frontend work on the TraceData capstone. It enforces architecture constraints, design standards, and implementation patterns aligned with your rubric (XRAI, Cybersecurity, Clean Architecture, Performance, Accessibility).

---

## 📐 PART 1: Architecture Constraints

### Core Stack

- **Backend**: Python (FastAPI + LangGraph) — Agentic AI Middleware Monolith
- **Frontend**: Next.js with App Router
- **Styling**: Tailwind CSS + Shadcn UI
- **Database**: PostgreSQL with pgvector (semantic search), Redis (caching), Celery (task queues)
- **Messaging**: Kafka (telematics), MQTT (device ingestion), WebSocket (real-time safety alerts)

### Multi-Tenancy (MANDATORY)

Every data layer must include and enforce `tenant_id`:

- **Telematics Data**: GPS, speed, RPM pings tagged with tenant
- **Driver Profiles**: Isolated per tenant
- **Trip Logs**: Segregated by tenant_id
- **Frontend Data Flow**: Verify `tenant_id` on every API call; never process data without it

**In API routes:**

```typescript
// src/pages/api/drivers.ts
const tenantId = req.headers["x-tenant-id"] || getUserTenant(token);
if (!tenantId)
  return res.status(403).json({ error: "Tenant context required" });
// Query with WHERE tenant_id = tenantId
```

### Ingestion & Data Pipelines

#### Telematics (High-Frequency)

- **Source**: Onboard Telematic Control Unit (TCU)
- **Frequency**: 10–30 second pings (GPS, speed, RPM, harsh events)
- **Batching**: Collated every 4–10 minutes (Normal Pipe)
- **Schema**: Flattened, sparse JSON (omit irrelevant fields to save bandwidth)
- **XAI Optimization**: Uniform `details` dictionary for downstream ML

**Ping Types:**

- `Emergency Ping` — Critical events (accidents, extreme braking)
- `Normal Ping` — Standard telemetry
- `Start of Trip Ping` — Trip initialization
- `End of Trip Ping` — Trip completion

**Critical Events Bypass**: High-severity anomalies (harsh braking, accidents) bypass batching and go immediately via Critical Events pipe.

**Incident Media**: AWS S3 URLs appended to critical event telemetry.

#### Unstructured Driver Input

- **Source**: Driver app (free-text reviews, feedback, formal appeals)
- **Routing**: Goes through Ingestion Quality Agent
- **Storage**: PostgreSQL with pgvector for semantic search

#### Frontend Integration

- Never assume data is immediately available; handle async loading states
- Telematics batches arrive every 4–10 minutes; refresh metrics accordingly
- Safety-critical alerts come via WebSocket from Kafka; display immediately with sub-500ms latency

### Context Enrichment (MCP)

- **Input**: Raw GPS coordinates, timestamps
- **Output**: Rich geographic data (Place Name, Topology, Weather, Traffic)
- **Tool Service**: Returns in < 2 seconds; used by Behavior, Safety, Orchestrator agents
- **Frontend Use**: Display location context and weather conditions in trip details, driver profiles

### Safety Intervention (Multi-Level)

Evaluated by Safety Agent on Critical Events:

- **Level 1 (Minor)**: App notification / in-cab reminder
- **Level 2 (Moderate)**: Formal message logged and sent to driver
- **Level 3 (Serious)**: Escalation/call to Fleet Manager

**Frontend**: Display safety levels with corresponding urgency (red for Level 3, orange for Level 2, yellow for Level 1)

### AI Security & Guardrails

- **LLM Rate Limiting**: Strict per-driver/per-tenant token quotas
- **Prompt Sanitization**: Explicit templating; sanitize all user input before passing to agents
- **Fairness Monitoring**: Track Statistical Parity Difference (SPD); alert if drift > 0.2
- **Data Privacy**: RBAC (JWT) for auth, AES-256 encryption for driver feedback

---

## 🎨 PART 2: Design System & Frontend Standards

### Core Design Philosophy

**Transparency through Design** — Premium, technical, yet accessible. Users trust what they can understand.

- **Aesthetics**: Glassmorphism (subtle background blurs), smooth gradients, high contrast
- **Feeling**: Command Center for fleet managers; Dashboard for drivers
- **Trust Signal**: Data clearly explained; no magic or black boxes

### Color Palette (Tailwind + CSS Variables)

Define in `src/styles/globals.css`:

```css
:root {
  /* Brand Colors */
  --brand-blue: hsl(210, 100%, 50%); /* Primary actions, manager focus */
  --brand-teal: hsl(174, 100%, 45%); /* Safety, success, driver positives */
  --brand-red: hsl(0, 84%, 60%); /* Critical errors, safety alerts */
  --brand-rose: hsl(10, 78%, 58%); /* Warnings, caution states */

  /* Semantic */
  --success: var(--brand-teal);
  --warning: var(--brand-rose);
  --error: var(--brand-red);
  --info: var(--brand-blue);

  /* Neutrals */
  --gray-50: hsl(0, 0%, 98%);
  --gray-100: hsl(0, 0%, 96%);
  --gray-200: hsl(0, 0%, 89%);
  --gray-900: hsl(0, 0%, 9%);
}

/* Glassmorphism backdrop */
.glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.3);
}
```

### Typography

- **Headers (Display)**: Bold, uppercase, tracked. Convey authority.
  - Font: SF Pro Display, `font-bold text-lg md:text-2xl uppercase tracking-tight`
- **Body (Roboto)**: Dense data, readable. `font-roboto text-base leading-relaxed`. Fallback to **SF Pro Text** where applicable.
- **Identifiers (Geist Mono)**: Trip IDs, vehicle IDs, metric values. `font-mono text-sm`
- **Emphasis**: Use weight variation (regular → semibold → bold) rather than italic

### Page Templates (NEVER START FROM SCRATCH)

#### [Template] DashboardPageTemplate

Root wrapper for dashboard overviews and standalone detail pages.

```typescript
// src/components/shared/DashboardPageTemplate.tsx
'use client';

import { ReactNode } from 'react';

interface DashboardPageTemplateProps {
  title: string;
  breadcrumbs?: { label: string; href: string }[];
  headerActions?: ReactNode;
  stats?: {
    label: string;
    value: string | number;
    change?: number;
    icon?: ReactNode;
  }[];
  children: ReactNode;
}

export function DashboardPageTemplate({
  title,
  breadcrumbs,
  headerActions,
  stats,
  children,
}: DashboardPageTemplateProps) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      {/* Breadcrumbs */}
      {breadcrumbs && (
        <nav className="mb-6 flex gap-2 text-sm text-gray-600">
          {breadcrumbs.map((bc) => (
            <a key={bc.href} href={bc.href} className="hover:text-gray-900">
              {bc.label}
            </a>
          ))}
        </nav>
      )}

      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold uppercase tracking-tight text-gray-900">
          {title}
        </h1>
        <div className="flex gap-3">{headerActions}</div>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 max-w-[1600px]">
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="glass rounded-lg p-6"
            >
              <p className="text-sm font-medium text-gray-600">{stat.label}</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">
                {stat.value}
              </p>
              {stat.change !== undefined && (
                <p className={`mt-1 text-xs font-semibold ${
                  stat.change >= 0 ? 'text-teal-600' : 'text-red-600'
                }`}>
                  {stat.change >= 0 ? '+' : ''}{stat.change}% from last period
                </p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-[1600px]">{children}</div>
    </div>
  );
}
```

**Usage:**

```typescript
export default function DriversPage() {
  return (
    <DashboardPageTemplate
      title="Fleet Drivers"
      breadcrumbs={[{ label: 'Home', href: '/' }, { label: 'Drivers', href: '/drivers' }]}
      headerActions={<Button>Add Driver</Button>}
      stats={[
        { label: 'Total Drivers', value: '24', change: 5 },
        { label: 'High Risk', value: '3', change: -1 },
        { label: 'Avg Score', value: '78.2', change: 2 },
      ]}
    >
      <DriverTable />
    </DashboardPageTemplate>
  );
}
```

#### [Template] DetailContentTemplate

Render consistent content within detail sheets or full-page detail views.

```typescript
// src/components/shared/DetailContentTemplate.tsx
'use client';

interface DetailContentTemplateProps {
  icon: ReactNode;
  id: string;
  status: 'active' | 'inactive' | 'alert' | 'critical';
  title: string;
  highlights?: {
    label: string;
    value: string | number;
    unit?: string;
  }[];
  sections?: {
    title: string;
    content: ReactNode;
  }[];
}

export function DetailContentTemplate({
  icon,
  id,
  status,
  title,
  highlights,
  sections,
}: DetailContentTemplateProps) {
  const statusColor = {
    active: 'bg-teal-100 text-teal-800',
    inactive: 'bg-gray-100 text-gray-800',
    alert: 'bg-rose-100 text-rose-800',
    critical: 'bg-red-100 text-red-800',
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="flex items-start gap-4">
        <div className="text-4xl">{icon}</div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
          <p className="mt-1 text-sm text-gray-600 font-mono">{id}</p>
          <span className={`mt-2 inline-block rounded px-3 py-1 text-xs font-semibold ${statusColor[status]}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>
      </div>

      {/* Highlights Grid */}
      {highlights && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
          {highlights.map((h) => (
            <div key={h.label} className="rounded bg-gray-50 p-3">
              <p className="text-xs font-medium text-gray-600">{h.label}</p>
              <p className="mt-1 text-lg font-bold text-gray-900">
                {h.value}
                {h.unit && <span className="text-sm text-gray-600"> {h.unit}</span>}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Content Sections */}
      {sections && (
        <div className="space-y-4">
          {sections.map((section) => (
            <div key={section.title} className="rounded border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900">{section.title}</h3>
              <div className="mt-3 text-sm text-gray-700">{section.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

### Component Standards

#### Rule 1: Shadcn UI First

Always use Shadcn components for consistent styling and accessibility:

- `<Button />` for all interactive buttons
- `<Table />` for data tables
- `<Sheet />` for side panels and detail views
- `<Dialog />` for modals
- `<Progress />` for progress indicators
- `<Tabs />` for multi-section views

#### Rule 2: Data Table Pattern

Overview pages must use a shared `DataTable` component with row-click selection:

```typescript
// src/components/shared/DataTable.tsx
'use client';

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface DataTableProps<T> {
  columns: {
    key: keyof T;
    label: string;
    render?: (value: T[keyof T], row: T) => ReactNode;
  }[];
  data: T[];
  onRowClick?: (row: T) => void;
  rowKey: keyof T;
}

export function DataTable<T>({
  columns,
  data,
  onRowClick,
  rowKey,
}: DataTableProps<T>) {
  return (
    <div className="rounded border border-gray-200 overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead key={String(col.key)} className="font-semibold text-gray-900">
                {col.label}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row) => (
            <TableRow
              key={String(row[rowKey])}
              onClick={() => onRowClick?.(row)}
              className={onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
            >
              {columns.map((col) => (
                <TableCell key={String(col.key)}>
                  {col.render ? col.render(row[col.key], row) : String(row[col.key])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
```

#### Rule 3: Detail Sheet Pattern

Record details must be shown in a `DetailSheet` occupying exactly **1/3** of viewport width:

```typescript
// src/components/shared/DetailSheet.tsx
'use client';

import { Sheet, SheetContent, SheetHeader, SheetTitle } from '@/components/ui/sheet';

interface DetailSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  children: ReactNode;
}

export function DetailSheet({
  open,
  onOpenChange,
  title,
  children,
}: DetailSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="sm:!w-[33.33vw] overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{title}</SheetTitle>
        </SheetHeader>
        <div className="mt-6">{children}</div>
      </SheetContent>
    </Sheet>
  );
}
```

#### Rule 4: No Native Buttons

Replace all `<button>` tags with `<Button />` from Shadcn:

```typescript
// ❌ WRONG
<button onClick={handleClick} className="px-4 py-2 bg-blue-600 text-white rounded">
  Click me
</button>

// ✅ CORRECT
import { Button } from '@/components/ui/button';

<Button onClick={handleClick} variant="default">
  Click me
</Button>
```

---

## 🚀 PART 3: Implementation Patterns

### Project Structure

```
src/
├── components/
│   ├── agents/                      # Agent-aware components
│   │   ├── orchestrator-view.tsx        # Queries Orchestrator Agent
│   │   ├── safety-alert-handler.tsx     # Listens to Kafka safety alerts
│   │   ├── feedback-agent-display.tsx   # Feedback & Advocacy Agent
│   │   └── context-enrichment-view.tsx  # Context Enrichment Tool Service
│   ├── explainability/              # XRAI rubric components
│   │   ├── shap-force-plot.tsx          # Feature contribution visualization
│   │   ├── lime-explanation.tsx         # Local interpretable explanations
│   │   ├── behavior-score-breakdown.tsx # XGBoost scoring rationale
│   │   └── fairness-audit-display.tsx   # AIF360 fairness metrics
│   ├── security/                    # Cybersecurity rubric components
│   │   ├── auth-guard.tsx
│   │   ├── api-request-validator.tsx
│   │   └── data-sanitizer.ts
│   ├── shared/                      # Reusable templates & UI elements
│   │   ├── DashboardPageTemplate.tsx
│   │   ├── DetailContentTemplate.tsx
│   │   ├── DetailSheet.tsx
│   │   ├── DataTable.tsx
│   │   ├── layout.tsx
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   └── error-boundary.tsx
│   ├── fleet-operator/              # Fleet operator UI
│   │   ├── vehicle-list.tsx
│   │   ├── driver-analytics.tsx
│   │   └── trip-detail.tsx
│   └── admin/                       # Admin/observability UI
│       ├── observability.tsx
│       ├── audit-logs.tsx
│       └── fairness-metrics.tsx
├── pages/
│   ├── api/
│   │   ├── agent-query.ts           # API route for Orchestrator Agent
│   │   ├── safety-events.ts         # WebSocket for Kafka safety alerts
│   │   └── explainability.ts        # SHAP/LIME explanation endpoints
│   ├── fleet-operator/
│   │   ├── dashboard.tsx
│   │   ├── vehicles/[id].tsx
│   │   └── reports.tsx
│   ├── admin/
│   │   ├── observability.tsx
│   │   ├── audit-logs.tsx
│   │   └── fairness-metrics.tsx
│   └── _.tsx                        # 404 catch-all
├── lib/
│   ├── agent-client.ts              # Typed client for agent backend
│   ├── types/
│   │   ├── agents.ts                # Agent-related types
│   │   ├── scoring.ts               # Driver behavior scoring types
│   │   ├── explainability.ts        # SHAP/LIME output schemas
│   │   └── safety.ts                # Safety alert types
│   ├── hooks/
│   │   ├── useAgentQuery.ts         # Hook for Orchestrator queries
│   │   ├── useSafetyAlerts.ts       # Hook for WebSocket safety events
│   │   └── useFairnessAudit.ts      # Hook for fairness metrics
│   ├── utils/
│   │   ├── security.ts              # Auth, validation, sanitization
│   │   ├── accessibility.ts         # ARIA helpers, keyboard nav
│   │   └── performance.ts           # Code splitting utilities
│   └── config/
│       ├── api-endpoints.ts         # Backend API endpoints
│       └── tailwind-theme.ts        # Design tokens
├── styles/
│   ├── globals.css                  # Global + Tailwind setup
│   └── colors.css                   # CSS variables (brand colors)
├── middleware.ts                    # Next.js middleware for security
└── next.config.js                   # Performance & security optimizations
```

### Component Anatomy

Every component should follow this structure:

```typescript
// src/components/example-component.tsx
'use client'; // Mark client components explicitly

import { FC, ReactNode } from 'react';
import { cn } from '@/lib/utils';

/**
 * ExampleComponent demonstrates:
 * - Explainability (XRAI): Shows why data matters
 * - Security (Cybersecurity): Input sanitization, safe props
 * - Accessibility (UX Quality): ARIA labels, keyboard nav
 * - Performance: Lazy rendering, memoization
 * - Clean Architecture: Single responsibility, typed props
 */
interface ExampleComponentProps {
  /** Primary content to display */
  title: string;
  /** Optional explanation for XRAI */
  explanation?: ReactNode;
  /** Accessibility label */
  ariaLabel?: string;
  /** CSS class extensions */
  className?: string;
}

export const ExampleComponent: FC<ExampleComponentProps> = ({
  title,
  explanation,
  ariaLabel,
  className,
}) => {
  return (
    <div
      className={cn(
        'rounded-lg border border-gray-200 p-4',
        'transition-shadow hover:shadow-md',
        className
      )}
      role="region"
      aria-label={ariaLabel || title}
    >
      <h2 className="font-semibold text-gray-900">{title}</h2>
      {explanation && (
        <details className="mt-2 cursor-pointer text-sm text-gray-600">
          <summary className="font-medium hover:text-gray-900">
            Why does this matter?
          </summary>
          <div className="mt-2 rounded bg-blue-50 p-3">{explanation}</div>
        </details>
      )}
    </div>
  );
};
```

**Key Principles**:

- Use `'use client'` for client-side interactivity; maximize server-side rendering
- Document rubric alignment in JSDoc comments
- Use TypeScript strict mode; no `any` types
- Use `cn()` utility for Tailwind merging
- Include ARIA labels and semantic HTML

### Agent-Aware Components (Clean Architecture)

Components interacting with agents must be explicitly aware of agent boundaries.

```typescript
// src/components/agents/orchestrator-view.tsx
'use client';

import { useCallback, useState } from 'react';
import { useAgentQuery } from '@/lib/hooks/useAgentQuery';
import { OrchestratorRequest, OrchestratorResponse } from '@/lib/types/agents';
import { Button } from '@/components/ui/button';

/**
 * OrchestratorView demonstrates agent integration:
 * - Makes queries to Orchestrator Agent (true LLM-controlled agent)
 * - Handles async responses with loading/error states
 * - RUBRIC: Clean Architecture—clear agent boundary
 *
 * Reference: A1 (Architecture Overview), A3 (Data Flow)
 */
export function OrchestratorView() {
  const [query, setQuery] = useState('');
  const { data, loading, error, mutate } = useAgentQuery<
    OrchestratorRequest,
    OrchestratorResponse
  >('/api/agent-query');

  const handleSubmitQuery = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      await mutate({ question: query });
      setQuery('');
    },
    [query, mutate]
  );

  return (
    <form onSubmit={handleSubmitQuery} className="space-y-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask the Orchestrator Agent..."
        aria-label="Query for Orchestrator Agent"
        className="w-full rounded border border-gray-300 px-3 py-2"
      />
      <Button type="submit" disabled={loading}>
        {loading ? 'Querying...' : 'Submit'}
      </Button>
      {error && <div className="rounded bg-red-50 p-3 text-red-800">{error.message}</div>}
      {data && (
        <div className="rounded bg-teal-50 p-3 text-teal-900">
          <p className="font-medium">Orchestrator Response:</p>
          <p className="mt-1">{data.result}</p>
        </div>
      )}
    </form>
  );
}
```

### Explainability Components (XRAI Rubric)

Every scoring, prediction, or recommendation must have a "why" explanation.

#### SHAP Force Plot

```typescript
// src/components/explainability/shap-force-plot.tsx
'use client';

import { useMemo } from 'react';

interface SHAPValue {
  featureName: string;
  value: number;
  contribution: 'positive' | 'negative';
  magnitude: number;
}

interface SHAPForcePlotProps {
  baseValue: number;
  shapeValues: SHAPValue[];
  predictionValue: number;
  modelName: string; // e.g., "Driver Behavior XGBoost"
}

/**
 * SHAPForcePlot visualizes SHAP feature contributions.
 * RUBRIC: XRAI—demonstrates how features contributed to prediction.
 * Reference: A5 (XGBoost Fairness & Explainability)
 */
export function SHAPForcePlot({
  baseValue,
  shapeValues,
  predictionValue,
  modelName,
}: SHAPForcePlotProps) {
  const { positiveForces, negativeForces, totalPositive, totalNegative } =
    useMemo(() => {
      const pos = shapeValues.filter((v) => v.contribution === 'positive');
      const neg = shapeValues.filter((v) => v.contribution === 'negative');
      return {
        positiveForces: pos,
        negativeForces: neg,
        totalPositive: pos.reduce((sum, v) => sum + v.magnitude, 0),
        totalNegative: neg.reduce((sum, v) => sum + v.magnitude, 0),
      };
    }, [shapeValues]);

  const maxMagnitude = Math.max(
    Math.abs(totalPositive),
    Math.abs(totalNegative)
  );

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6">
      <h3 className="mb-4 font-semibold text-gray-900">
        SHAP Force Plot: {modelName}
      </h3>

      {/* Legend */}
      <div className="mb-4 flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-red-500" />
          <span className="text-gray-700">Negative impact</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-teal-500" />
          <span className="text-gray-700">Positive impact</span>
        </div>
      </div>

      {/* Base value → Prediction flow */}
      <div className="mb-6 rounded bg-gray-50 p-4">
        <div className="flex items-center justify-between">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Base Value</p>
            <p className="text-lg font-bold text-gray-900">{baseValue.toFixed(3)}</p>
          </div>
          <div className="flex-1 px-4">
            {/* Positive contributions */}
            {positiveForces.length > 0 && (
              <div className="flex items-center mb-2">
                <div className="text-xs font-semibold text-teal-600">
                  +{totalPositive.toFixed(3)}
                </div>
                <div
                  className="h-2 rounded bg-teal-500 ml-2"
                  style={{
                    width: `${(Math.abs(totalPositive) / maxMagnitude) * 100}%`,
                  }}
                />
              </div>
            )}
            {/* Negative contributions */}
            {negativeForces.length > 0 && (
              <div className="flex items-center">
                <div className="text-xs font-semibold text-red-600">
                  {totalNegative.toFixed(3)}
                </div>
                <div
                  className="h-2 rounded bg-red-500 ml-2"
                  style={{
                    width: `${(Math.abs(totalNegative) / maxMagnitude) * 100}%`,
                  }}
                />
              </div>
            )}
          </div>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Prediction</p>
            <p className="text-lg font-bold text-gray-900">
              {predictionValue.toFixed(3)}
            </p>
          </div>
        </div>
      </div>

      {/* Feature contributions table */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-600">Top Contributing Features</p>
        <div className="max-h-60 overflow-y-auto rounded border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="px-3 py-2 text-left font-medium text-gray-700">
                  Feature
                </th>
                <th className="px-3 py-2 text-right font-medium text-gray-700">
                  Value
                </th>
                <th className="px-3 py-2 text-right font-medium text-gray-700">
                  Impact
                </th>
              </tr>
            </thead>
            <tbody>
              {shapeValues
                .sort((a, b) => Math.abs(b.magnitude) - Math.abs(a.magnitude))
                .slice(0, 10)
                .map((force) => (
                  <tr key={force.featureName} className="border-b hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-900">{force.featureName}</td>
                    <td className="px-3 py-2 text-right text-gray-700">
                      {force.value.toFixed(2)}
                    </td>
                    <td className="px-3 py-2 text-right font-semibold">
                      <span
                        className={
                          force.contribution === 'positive'
                            ? 'text-teal-600'
                            : 'text-red-600'
                        }
                      >
                        {force.contribution === 'positive' ? '+' : ''}
                        {force.magnitude.toFixed(3)}
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explainability statement */}
      <div className="mt-4 rounded bg-blue-50 p-3 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">What does this mean?</p>
        <p className="mt-1">
          This SHAP force plot shows how each feature pushed the prediction up
          (teal) or down (red) from the base value. See A5 for model details and
          AIF360 fairness audits.
        </p>
      </div>
    </div>
  );
}
```

#### LIME Explanation

```typescript
// src/components/explainability/lime-explanation.tsx
'use client';

interface LIMEWeight {
  featureName: string;
  weight: number;
  direction: 'supports' | 'opposes';
}

interface LIMEExplanationProps {
  prediction: string;
  confidence: number;
  weights: LIMEWeight[];
  instanceIndex: number;
}

/**
 * LIMEExplanation shows local interpretable model-agnostic explanations.
 * RUBRIC: XRAI—human-friendly per-instance explanations.
 */
export function LIMEExplanation({
  prediction,
  confidence,
  weights,
  instanceIndex,
}: LIMEExplanationProps) {
  return (
    <div className="space-y-4 rounded-lg border border-gray-200 bg-white p-6">
      <div>
        <h3 className="font-semibold text-gray-900">
          LIME Explanation (Instance #{instanceIndex})
        </h3>
        <p className="mt-1 text-sm text-gray-600">
          Local Interpretable Model-Agnostic Explanation
        </p>
      </div>

      {/* Prediction badge */}
      <div className="rounded bg-gray-50 p-4">
        <p className="text-sm text-gray-600">Predicted Class</p>
        <div className="mt-1 flex items-center gap-3">
          <span className="text-xl font-bold text-gray-900">{prediction}</span>
          <div className="h-2 w-24 rounded bg-gray-200">
            <div
              className="h-full rounded bg-blue-600"
              style={{ width: `${confidence * 100}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700">
            {(confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Feature importance */}
      <div className="space-y-3">
        <p className="text-sm font-medium text-gray-600">Feature Importance</p>
        {weights
          .sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight))
          .map((w) => (
            <div key={w.featureName} className="flex items-center gap-3">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">
                  {w.featureName}
                </p>
                <p className="text-xs text-gray-500">
                  {w.direction === 'supports'
                    ? 'Supports prediction'
                    : 'Opposes prediction'}
                </p>
              </div>
              <div className="h-2 w-16 rounded bg-gray-200">
                <div
                  className={`h-full rounded ${
                    w.direction === 'supports' ? 'bg-teal-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.abs(w.weight) * 100}%` }}
                />
              </div>
              <span className="w-12 text-right text-sm font-semibold text-gray-700">
                {w.weight.toFixed(3)}
              </span>
            </div>
          ))}
      </div>

      {/* Fairness context */}
      <div className="rounded bg-amber-50 p-3 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">Fairness Context</p>
        <p className="mt-1">
          Generated with AIF360 bias audits. See A5 for Statistical Parity
          Difference metrics.
        </p>
      </div>
    </div>
  );
}
```

#### Behavior Score Breakdown

```typescript
// src/components/explainability/behavior-score-breakdown.tsx
'use client';

import { useMemo } from 'react';
import { Progress } from '@/components/ui/progress';

interface ScoreComponent {
  name: string;
  category: 'acceleration' | 'braking' | 'cornering' | 'speed' | 'other';
  rawScore: number;
  normalizedScore: number;
  weight: number;
}

interface BehaviorScoreBreakdownProps {
  driverId: string;
  totalScore: number;
  components: ScoreComponent[];
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

/**
 * BehaviorScoreBreakdown shows XGBoost scoring decomposed.
 * RUBRIC: XRAI—allows fleet operators to understand scoring rationale.
 * RUBRIC: Performance—memoized computation for large datasets.
 */
export function BehaviorScoreBreakdown({
  driverId,
  totalScore,
  components,
  riskLevel,
}: BehaviorScoreBreakdownProps) {
  const contribution = useMemo(() => {
    return components.map((c) => ({
      ...c,
      percentOfTotal: (c.normalizedScore * c.weight) / totalScore,
    }));
  }, [components, totalScore]);

  const riskColor = {
    low: 'bg-teal-100 text-teal-800 border-teal-300',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    high: 'bg-rose-100 text-rose-800 border-rose-300',
    critical: 'bg-red-100 text-red-800 border-red-300',
  };

  return (
    <div className="space-y-6 rounded-lg border border-gray-200 bg-white p-6">
      <div>
        <h3 className="font-semibold text-gray-900">
          Driver Behavior Score Breakdown
        </h3>
        <p className="mt-1 text-sm text-gray-600 font-mono">
          Driver ID: {driverId}
        </p>
      </div>

      {/* Overall score badge */}
      <div className={`rounded-lg border p-4 ${riskColor[riskLevel]}`}>
        <p className="text-sm font-medium">Overall Safety Score</p>
        <p className="mt-1 text-3xl font-bold">{totalScore.toFixed(1)}</p>
        <p className="mt-2 text-sm font-semibold uppercase">
          {riskLevel} Risk
        </p>
      </div>

      {/* Component breakdown */}
      <div className="space-y-4">
        <p className="text-sm font-medium text-gray-600">Score Components</p>
        {contribution
          .sort((a, b) => b.percentOfTotal - a.percentOfTotal)
          .map((comp) => (
            <div key={comp.name} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">{comp.name}</span>
                <span className="text-gray-900">
                  {comp.normalizedScore.toFixed(1)} pts
                </span>
              </div>
              <Progress value={comp.percentOfTotal * 100} />
              <p className="text-xs text-gray-500">
                Weight: {(comp.weight * 100).toFixed(0)}% • Category: {comp.category}
              </p>
            </div>
          ))}
      </div>

      {/* Methodology */}
      <div className="rounded bg-blue-50 p-4 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">Scoring Methodology</p>
        <ul className="mt-2 list-inside space-y-1 list-disc text-gray-600">
          <li>Model: XGBoost (see A5)</li>
          <li>Features: Telematics from ingestion pipeline</li>
          <li>Fairness: AIF360 Statistical Parity Difference audit</li>
          <li>Updates: Real-time as new trip data arrives</li>
        </ul>
      </div>
    </div>
  );
}
```

### Security Components (Cybersecurity Rubric)

```typescript
// src/lib/utils/security.ts
import DOMPurify from "isomorphic-dompurify";

/**
 * Security utilities for TraceData.
 * RUBRIC: Cybersecurity—input validation, sanitization, CSP.
 */

/** Validate JWT token structure */
export function isValidJWT(token: string): boolean {
  const parts = token.split(".");
  return parts.length === 3 && parts.every((p) => p.length > 0);
}

/** Sanitize user-provided HTML */
export function sanitizeHTML(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ["b", "i", "em", "strong", "p", "br", "ul", "li", "a"],
    ALLOWED_ATTR: ["href", "target"],
  });
}

/** Escape user input for safe display */
export function escapeUserInput(input: string): string {
  const div = document.createElement("div");
  div.textContent = input;
  return div.innerHTML;
}

/** Verify API request origin */
export function isAllowedOrigin(
  origin: string,
  allowedOrigins: string[],
): boolean {
  return allowedOrigins.includes(origin);
}

/** Rate limiting key from request */
export function getRateLimitKey(req: { headers: Headers }): string {
  return req.headers.get("x-forwarded-for") || "unknown";
}

/** Secure headers for CSP and protection */
export const secureHeaders = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self'",
    "connect-src 'self' https://api.tracedata.local",
    "frame-ancestors 'none'",
  ].join("; "),
};
```

API route with security:

```typescript
// src/pages/api/agent-query.ts
import { NextApiRequest, NextApiResponse } from "next";
import { isValidJWT, secureHeaders } from "@/lib/utils/security";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  // Set security headers
  Object.entries(secureHeaders).forEach(([key, value]) => {
    res.setHeader(key, value);
  });

  // Validate tenant context
  const tenantId = req.headers["x-tenant-id"] as string;
  if (!tenantId) {
    return res.status(403).json({ error: "Tenant context required" });
  }

  // Only POST
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  // Validate JWT
  const token = req.headers.authorization?.split(" ")[1];
  if (!token || !isValidJWT(token)) {
    return res.status(401).json({ error: "Unauthorized" });
  }

  // Validate request body
  const { question } = req.body;
  if (!question || typeof question !== "string" || question.length > 500) {
    return res.status(400).json({ error: "Invalid request" });
  }

  try {
    // Call Orchestrator Agent with tenant context
    const response = await fetch(
      `${process.env.BACKEND_URL}/api/orchestrator-query`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          "x-tenant-id": tenantId,
        },
        body: JSON.stringify({ question }),
      },
    );

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error("Agent query error:", error);
    return res.status(500).json({ error: "Internal server error" });
  }
}
```

### Accessibility Utilities (UX Quality)

```typescript
// src/lib/utils/accessibility.ts

/**
 * Accessibility utilities for WCAG 2.1 AA compliance.
 * RUBRIC: UX Quality—keyboard navigation, ARIA labels, contrast.
 */

/** Generate ARIA label for complex components */
export function generateAriaLabel(context: {
  action: string;
  subject: string;
  status?: string;
}): string {
  const parts = [context.action, context.subject, context.status].filter(
    Boolean,
  );
  return parts.join(": ");
}

/** Announce screen reader messages */
export function announceScreenReader(
  message: string,
  priority: "polite" | "assertive" = "polite",
) {
  const div = document.createElement("div");
  div.setAttribute("role", "status");
  div.setAttribute("aria-live", priority);
  div.className = "sr-only";
  div.textContent = message;
  document.body.appendChild(div);
  setTimeout(() => div.remove(), 1000);
}

/** Keyboard navigation handler */
export function useKeyboardNavigation(
  onEnter: () => void,
  onEscape: () => void,
) {
  return (e: React.KeyboardEvent) => {
    if (e.key === "Enter") onEnter();
    if (e.key === "Escape") onEscape();
  };
}
```

### Performance Patterns

#### Code Splitting & Lazy Loading

```typescript
// src/pages/admin/observability.tsx
import dynamic from 'next/dynamic';
import { Suspense } from 'react';

// Lazy-load heavy observability dashboards
const FairnessMetricsDashboard = dynamic(
  () => import('@/components/admin/fairness-metrics'),
  {
    loading: () => <div className="p-4">Loading metrics...</div>,
  }
);

const AuditLogViewer = dynamic(
  () => import('@/components/admin/audit-logs'),
  {
    loading: () => <div className="p-4">Loading logs...</div>,
  }
);

export default function ObservabilityPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="space-y-6 p-6">
        <FairnessMetricsDashboard />
        <AuditLogViewer />
      </div>
    </Suspense>
  );
}
```

#### Data Fetching with SWR

```typescript
// src/lib/hooks/useAgentQuery.ts
import useSWR from "swr";

const fetcher = (url: string) =>
  fetch(url, {
    headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
  }).then((r) => r.json());

export function useAgentQuery<T, R>(url: string) {
  const { data, error, isLoading, mutate } = useSWR<R>(url, fetcher, {
    revalidateOnFocus: false,
    dedupingInterval: 5000, // Cache for 5s
  });

  return {
    data,
    loading: isLoading,
    error,
    mutate,
  };
}
```

#### WebSocket for Real-Time Safety Alerts

```typescript
// src/lib/hooks/useSafetyAlerts.ts
import { useEffect, useState, useCallback } from "react";

interface SafetyAlert {
  eventId: string;
  driverId: string;
  severity: "warning" | "critical";
  message: string;
  timestamp: string;
  tenantId: string;
}

/**
 * Hook for real-time safety alerts from Kafka via WebSocket.
 * RUBRIC: Performance—uses WebSocket for sub-500ms alerts.
 * RUBRIC: Clean Architecture—demonstrates Kafka boundary from A16.
 */
export function useSafetyAlerts(tenantId: string) {
  const [alerts, setAlerts] = useState<SafetyAlert[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket(
      `${process.env.NEXT_PUBLIC_WS_URL}/safety-events?tenant=${tenantId}`,
    );

    ws.onopen = () => setConnected(true);
    ws.onmessage = (event) => {
      const alert: SafetyAlert = JSON.parse(event.data);
      // Multi-tenancy check
      if (alert.tenantId === tenantId) {
        setAlerts((prev) => [alert, ...prev].slice(0, 100)); // Keep last 100
      }
    };
    ws.onerror = () => setConnected(false);
    ws.onclose = () => setConnected(false);

    return () => ws.close();
  }, [tenantId]);

  const clearAlert = useCallback((eventId: string) => {
    setAlerts((prev) => prev.filter((a) => a.eventId !== eventId));
  }, []);

  return { alerts, connected, clearAlert };
}
```

---

## 🎯 Common Tasks & Workflows

### Task 1: Create a New Fleet Operator Dashboard

```typescript
// src/pages/fleet-operator/dashboard.tsx
'use client';

import { DashboardPageTemplate } from '@/components/shared/DashboardPageTemplate';
import { DataTable } from '@/components/shared/DataTable';
import { Button } from '@/components/ui/button';
import { useAgentQuery } from '@/lib/hooks/useAgentQuery';
import { useSafetyAlerts } from '@/lib/hooks/useSafetyAlerts';

export default function FleetDashboard() {
  const { data: drivers, loading } = useAgentQuery('/api/drivers');
  const { alerts } = useSafetyAlerts('tenant-123');

  return (
    <DashboardPageTemplate
      title="Fleet Dashboard"
      breadcrumbs={[
        { label: 'Home', href: '/' },
        { label: 'Fleet', href: '/fleet-operator' },
      ]}
      headerActions={<Button>Add Driver</Button>}
      stats={[
        { label: 'Total Drivers', value: drivers?.length || 0 },
        { label: 'Critical Alerts', value: alerts.filter(a => a.severity === 'critical').length },
        { label: 'Avg Safety Score', value: '78.4' },
      ]}
    >
      {!loading && drivers ? (
        <DataTable
          columns={[
            { key: 'name', label: 'Driver Name' },
            { key: 'score', label: 'Safety Score' },
            { key: 'status', label: 'Status' },
          ]}
          data={drivers}
          rowKey="id"
          onRowClick={(driver) => {
            // Open detail sheet
          }}
        />
      ) : (
        <div>Loading...</div>
      )}
    </DashboardPageTemplate>
  );
}
```

### Task 2: Display SHAP Explanations for Driver Scores

Use the `SHAPForcePlot` component from explainability:

```typescript
import { SHAPForcePlot } from '@/components/explainability/shap-force-plot';

export function DriverScoreCard({ driverId }: Props) {
  const { data: shap } = useAgentQuery(`/api/explainability/shap/${driverId}`);

  return (
    <SHAPForcePlot
      baseValue={shap?.baseValue || 0}
      shapeValues={shap?.values || []}
      predictionValue={shap?.prediction || 0}
      modelName="Driver Behavior XGBoost"
    />
  );
}
```

### Task 3: Implement Real-Time Safety Alerts

```typescript
import { useSafetyAlerts } from '@/lib/hooks/useSafetyAlerts';

export function SafetyAlertPanel({ tenantId }: Props) {
  const { alerts, clearAlert } = useSafetyAlerts(tenantId);

  return (
    <div className="space-y-2">
      {alerts.map((alert) => (
        <div
          key={alert.eventId}
          className={`rounded p-4 ${
            alert.severity === 'critical'
              ? 'bg-red-100 text-red-900'
              : 'bg-yellow-100 text-yellow-900'
          }`}
        >
          <p className="font-semibold">{alert.message}</p>
          <p className="text-sm">{alert.driverId} • {alert.timestamp}</p>
          <button
            onClick={() => clearAlert(alert.eventId)}
            className="mt-2 text-sm underline"
          >
            Dismiss
          </button>
        </div>
      ))}
    </div>
  );
}
```

### Task 4: Add Multi-Tenancy to a New Page

```typescript
// src/pages/api/drivers.ts
import { NextApiRequest, NextApiResponse } from "next";

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse,
) {
  // Extract and validate tenant
  const tenantId = req.headers["x-tenant-id"] as string;
  if (!tenantId) {
    return res.status(403).json({ error: "Tenant context required" });
  }

  // Query database with tenant isolation
  const drivers = await db.drivers.findMany({
    where: { tenantId },
  });

  return res.status(200).json(drivers);
}
```

---

## ✅ Rubric Alignment Checklist

As you code, ensure every component addresses at least **one rubric area**:

### XRAI (Explainability)

- [ ] Components explain their data/logic via tooltips or expandable details
- [ ] SHAP/LIME visualizations for model scoring
- [ ] Driver Behavior Score breakdowns with clear rationale
- [ ] Fairness metrics displayed transparently
- [ ] Reference A5 for model details

### Cybersecurity

- [ ] API calls authenticated with valid JWT
- [ ] Tenant context (`x-tenant-id`) validated on every request
- [ ] User input validated and sanitized (no XSS)
- [ ] CSP headers configured in middleware/API routes
- [ ] Sensitive data never logged or exposed in frontend
- [ ] Rate limiting on agent queries

### Clean Architecture

- [ ] Components clearly marked as agent-aware vs. deterministic
- [ ] Single responsibility—one component, one job
- [ ] Typed props; no `any` types
- [ ] Hooks encapsulate backend communication
- [ ] Agent boundary clearly defined (A20 agency classification)

### Performance

- [ ] Code-split admin/observability dashboards (lazy load)
- [ ] Images optimized with Next.js Image
- [ ] API responses cached with SWR
- [ ] Bundle size monitored (use `next/bundle-analyzer`)
- [ ] WebSocket for real-time updates (sub-500ms latency)

### Accessibility (UX Quality)

- [ ] All interactive elements keyboard-navigable
- [ ] ARIA labels for screen readers
- [ ] Color contrast ≥4.5:1 (WCAG AA)
- [ ] Focus states visible and clear
- [ ] Semantic HTML throughout

---

## 📚 References & Documentation

**Architecture & Design**:

- **A1 (Architecture Overview)**: Six-agent system; Orchestrator Agent is primary control point
- **A2 (Database Schemas)**: Table structures for fleet, drivers, trips, scoring
- **A3 (Data Flow with Timing Proof)**: Timing SLAs; frontend must not block agent responses
- **A4 (Implementation Guide)**: Pattern-based folder structure (agents/ vs. services/)
- **A5 (XGBoost Fairness & Explainability)**: Model details, AIF360 audits, SHAP/LIME
- **A16 (Safety Architecture)**: Two-layer Safety Agent; Kafka boundary
- **A20 (Agency Classification)**: Agent vs. tool distinction

**Standards**:

- Tailwind CSS: https://tailwindcss.com/
- Shadcn UI: https://ui.shadcn.com/
- Next.js: https://nextjs.org/
- WCAG 2.1 AA: https://www.w3.org/WAI/WCAG21/quickref/

---

## 🔧 Directives for Your IDE Agent

When scaffolding new code:

1. **Always verify constraints**: Confirm new services fit within Python FastAPI + LangGraph + Next.js boundary
2. **Tenant context first**: Never process data without validated `tenant_id`
3. **Templates, not scratch**: Use `DashboardPageTemplate`, `DetailContentTemplate`, `DataTable`, `DetailSheet`
4. **No native buttons**: Always `<Button />` from Shadcn
5. **Document rubric alignment**: Every component should note which rubric area it addresses
6. **Reference architecture docs**: Comment with A1–A5, A16, A20 references
7. **Security by default**: Input validation, JWT checks, sanitization on user inputs
8. **Explain the "why"**: Especially for scoring/predictions—use SHAP/LIME
9. **Accessibility counts**: ARIA labels, keyboard nav, contrast checks
10. **Performance matters**: Lazy load heavy components, cache API responses, use WebSocket for real-time

---

**Last Updated**: March 2026  
**For**: TraceData Capstone Project (NUS-ISS SWE5008)  
**Authors**: Team guidance for Sree, P2, P3, P4
