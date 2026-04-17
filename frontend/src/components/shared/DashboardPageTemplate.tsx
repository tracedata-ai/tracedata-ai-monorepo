"use client";

import type { ReactNode } from "react";

type Stat = {
  label: string;
  value: string | number;
  change?: number;
};

type DashboardPageTemplateProps = {
  title: string;
  subtitle?: string;
  headerActions?: ReactNode;
  stats?: Stat[];
  children: ReactNode;
};

export function DashboardPageTemplate({
  title,
  subtitle,
  headerActions,
  stats,
  children,
}: DashboardPageTemplateProps) {
  return (
    <div className="min-h-full bg-background p-4 md:p-6">
      <div className="mx-auto max-w-[1600px]">
        <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-lg font-bold uppercase tracking-tight text-foreground md:text-2xl">
              {title}
            </h1>
            {subtitle ? (
              <p className="mt-1 text-sm text-muted-foreground">{subtitle}</p>
            ) : null}
          </div>
          {headerActions ? (
            <div className="flex gap-2">{headerActions}</div>
          ) : null}
        </div>

        {stats?.length ? (
          <div className="mb-6 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {stats.map((stat) => (
              <div key={stat.label} className="rounded-lg border border-border bg-card p-5 shadow-sm">
                <p className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </p>
                <p className="mt-2 text-2xl font-bold text-foreground">
                  {stat.value}
                </p>
                {stat.change !== undefined ? (
                  <p
                    className={`mt-1 text-xs font-semibold ${
                      stat.change >= 0
                        ? "text-[var(--success)]"
                        : "text-[var(--error)]"
                    }`}
                  >
                    {stat.change >= 0 ? "+" : ""}
                    {stat.change}% from last period
                  </p>
                ) : null}
              </div>
            ))}
          </div>
        ) : null}

        <div className="max-w-[1600px]">{children}</div>
      </div>
    </div>
  );
}
