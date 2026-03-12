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
