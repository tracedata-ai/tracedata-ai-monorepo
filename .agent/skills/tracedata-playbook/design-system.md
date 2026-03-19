# TraceData Design System

This module defines the design philosophy, color system, typography, and core page templates.

## Core Design Philosophy

**Transparency through Design** — Premium, technical, yet accessible. Users trust what they can understand.

- **Aesthetics**: Glassmorphism (subtle background blurs), smooth gradients, high contrast
- **Feeling**: Command Center for fleet managers; Dashboard for drivers
- **Trust Signal**: Data clearly explained; no magic or black boxes

## Color Palette (Tailwind + CSS Variables)

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

## Typography

- **Headers (Display)**: Bold, tracking tightened. Convey authority.
  - Font: Inter, `font-bold text-lg md:text-2xl tracking-tight`
- **Body (Inter)**: Clean, professional, highly readable. Use `font-sans` (mapped to Inter).
- **Identifiers & Metrics**: Use semibold weight for numeric clarity. `font-semibold text-sm`
- **Emphasis**: Use weight variation (regular → semibold → bold) rather than italic

## Page Templates

### DashboardPageTemplate

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
            <div key={stat.label} className="glass rounded-lg p-6">
              <p className="text-sm font-medium text-gray-600">{stat.label}</p>
              <p className="mt-2 text-2xl font-bold text-gray-900">{stat.value}</p>
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

### StatCard

Standardized card for displaying analytics and metrics.

```typescript
import { StatCard } from "@/components/shared/StatCard";

<StatCard
  title="Active Now"
  value={98}
  icon={ActivityIcon}
  iconClassName="text-slate-500"
  description="Up 12% from last hour"
/>
```

## Component Standards

### Rule 1: Shadcn UI First

Always use Shadcn components for consistency.

### Rule 2: Data Table Pattern

Use TanStack Table (v8) via `src/components/shared/DataTable.tsx`.

### Rule 3: Detail Sheet Pattern

Details must be shown in a `DetailSheet` (1/3 viewport width).

### Rule 4: No Native Buttons

Always use `<Button />` from Shadcn.

---

## Homepage (Marketing / Landing Page) Design System

The homepage (`frontend/src/app/page.tsx`) uses a **separate, dark-first design language** distinct from the dashboard. Do not mix dashboard Shadcn patterns with homepage styles.

### Font Trio

```tsx
import { JetBrains_Mono, Manrope, Sora } from "next/font/google";

const displayFont = Sora({ subsets: ["latin"], weight: ["600","700","800"] });  // headings
const bodyFont   = Manrope({ subsets: ["latin"], weight: ["400","500","600","700"] }); // body
const monoFont   = JetBrains_Mono({ subsets: ["latin"], weight: ["500","600"] }); // badges, code, labels
```

### Dark Navy Palette

| Token | Hex | Usage |
|---|---|---|
| `--bg-base` | `#0c1030` | Page background, section bg alternating |
| `--bg-deep` | `#070a2b` | Deeper sections (Explainability, TechSpecs, CTA) |
| `--bg-card` | `#151939` | Card backgrounds |
| `--bg-hover` | `#191d3d` | Card hover state |
| `--bg-panel` | `#232748` | Dashboard mock panels |
| `--accent-blue` | `#70d2ff` | Primary brand accent, borders, icons |
| `--accent-sky` | `#00aadd` | Gradient end color |
| `--accent-lavender` | `#a5c8ff` | Secondary icons, scale icons |
| `--accent-purple` | `#ddb7ff` | Tertiary icons, sentiment/orchestrator |
| `--text-primary` | `#dfe0ff` | Headings |
| `--text-muted` | `#bdc8d0` | Body descriptions |
| `--border-subtle` | `#3d484f` | Card borders, dividers |

### Animation System (`globals.css`)

**Philosophy:** Use CSS animations for the homepage (GPU compositor, zero JS bundle cost). Reserve Framer Motion for dashboard interactive UIs (modals, page transitions, AnimatePresence).

#### Scroll-triggered Fade-In-Up

```css
/* Base state — invisible, shifted down */
.fade-in-up {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.65s cubic-bezier(0.22, 1, 0.36, 1),
              transform 0.65s cubic-bezier(0.22, 1, 0.36, 1);
}
/* Triggered by JS adding .is-visible via IntersectionObserver */
.fade-in-up.is-visible { opacity: 1; transform: translateY(0); }
```

#### Stagger Delays

```css
/* Apply .stagger-N alongside .fade-in-up on each card (N = 1–8) */
.stagger-1 { transition-delay: 0.05s; }
.stagger-2 { transition-delay: 0.12s; }
/* ... up to stagger-8 at 0.54s */
```

#### Key Keyframes

| Keyframe | Class | Effect |
|---|---|---|
| `pulse-ring` | `.pulse-ring` | Ripple ring from element (Safety Agent icon) |
| `float` | `.orb-float-a` | Slow vertical drift for ambient background orbs |
| `float-slow` | `.orb-float-b` | Slower variant, offset `animation-delay: -4s` |
| `shimmer` | `.shimmer-badge` | One-time left-to-right shine sweep (hero badge on load) |
| `bar-grow` | `.shap-bar` + `.is-visible` | SHAP bars grow from `scaleY(0)→1` with spring easing |

#### Card Gradient Glow (Hover)

```css
/* Add .card-glow to any dark card for a soft gradient border on hover */
.card-glow::before {
  content: ''; position: absolute; inset: 0; border-radius: inherit;
  opacity: 0; transition: opacity 0.35s ease;
}
.card-glow:hover::before {
  opacity: 1;
  background: linear-gradient(135deg,
    rgba(112,210,255,0.5), rgba(165,200,255,0.3), rgba(221,183,255,0.4));
}
```

### Scroll Progress Bar

Always present at `z-[60]` above the sticky nav, 2px tall gradient bar:

```tsx
<div className="pointer-events-none fixed left-0 top-0 z-[60] h-[2px] w-full">
  <div
    className="h-full bg-gradient-to-r from-[#70d2ff] via-[#a5c8ff] to-[#00aadd] transition-[width] duration-100"
    style={{ width: `${scrollProgress}%` }}
  />
</div>
```

### Framer Motion Decision Rule

| Scenario | Use |
|---|---|
| Homepage landing animations (fade-in, stagger, scroll-trigger) | ✅ CSS + IntersectionObserver |
| Dashboard page transitions, route changes | ✅ Framer Motion (`AnimatePresence`) |
| Modal / drawer enter/exit | ✅ Framer Motion |
| Drag-to-reorder, spring physics | ✅ Framer Motion |
| Static hover effects, gradient borders | ✅ CSS only |

---

## Agent Flow Page Design System

The Agent Flow page (`/fleet-manager/agent-flow`) uses a **light GitHub Actions aesthetic** completely distinct from the dark dashboard and dark homepage. Do NOT apply dark navy tokens here.

### Palette

| Token | Hex | Usage |
|---|---|---|
| Page/canvas bg | `#f9fafb` | All backgrounds |
| Card bg | `#ffffff` | Node cards |
| Border default | `#e5e7eb` | Cards, separators, Controls |
| Border hover | `#d1d5db` | Node/button hover |
| Text primary | `#111827` | Agent label |
| Text muted | `#6b7280` | Subtitles, legend labels |
| Text faint | `#9ca3af` | Footer, status timestamps |

### Node Type — Left-Border Accent

| Type | Colour | Hex |
|---|---|---|
| `source` | Blue | `#3b82f6` |
| `tool` | Purple | `#8b5cf6` |
| `agent` | Indigo | `#6366f1` |
| `queue` | Amber | `#f59e0b` |
| `output` | Green | `#22c55e` |

### Status Badge Colours (Light)

| Status | Text | Background | Ring |
|---|---|---|---|
| `idle` | `#6b7280` | `#f3f4f6` | `#d1d5db/60` |
| `running` | `#d97706` | `#fef3c7` | `#f59e0b/40` |
| `success` | `#16a34a` | `#dcfce7` | `#22c55e/40` |
| `warning` | `#ea580c` | `#ffedd5` | `#fb923c/40` |
| `error` | `#dc2626` | `#fee2e2` | `#ef4444/40` |

### Edge Colours

| Path | Stroke |
|---|---|
| Default | `#d1d5db` |
| Orchestrator → Queue | `#6366f1` (indigo) |
| Safety edges | `#fca5a5` (soft rose) |

### React Flow Rules

1. **Always `dynamic` import with `ssr: false`** — React Flow uses browser DOM APIs not available in SSR.
2. **NodeTypes cast**: `const nodeTypes: NodeTypes = { agentNode: AgentNode as NodeTypes[string] }` — required to satisfy `@xyflow/react` v12's internal generic constraint.
3. **Bare `NodeProps`** for custom nodes — cast `props.data as YourDataType` inside the component body instead of using the generic `NodeProps<T>`.
4. **`proOptions={{ hideAttribution: true }}`** on `<ReactFlow>` to suppress the watermark in non-OSS usage.

```tsx
// Correct pattern for a custom node
function MyNode(props: NodeProps) {
  const data = props.data as MyNodeData;
  // ... render
}
export const MyNode = memo(MyNodeComponent);
```

```tsx
// Correct page-level dynamic import
const AgentFlowCanvas = dynamic(
  () => import("@/components/agent-flow/AgentFlowCanvas").then((m) => m.AgentFlowCanvas),
  { ssr: false }
);
```

### Simulation Pattern

When live backend data is unavailable, use an `setInterval`-based simulation hook to cycle node statuses:

```tsx
useEffect(() => {
  if (!simulating) return;
  const id = setInterval(() => {
    setNodes((prev) => /* pick a random agent node and advance its status */);
  }, 2000);
  return () => clearInterval(id);
}, [simulating, setNodes]);
```

Expose a `simulating: boolean` prop from the page layer — toggle via a Pause/Simulate button in the top bar.

