"use client";

import React from "react";
import { DashboardSection } from "./DashboardSection";
import { Separator } from "@/components/ui/separator";

interface DashboardPageTemplateProps {
  title: string;
  description?: string;
  headerActions?: React.ReactNode;
  stats?: React.ReactNode;
  filters?: React.ReactNode;
  breadcrumbs?: React.ReactNode;
  children: React.ReactNode;
}

export function DashboardPageTemplate({
  title,
  description,
  headerActions,
  stats,
  filters,
  breadcrumbs,
  children,
}: DashboardPageTemplateProps) {
  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      <main className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-200 dark:scrollbar-thumb-slate-800 scrollbar-track-transparent">
        <header className="bg-white dark:bg-slate-900 border-b border-border sticky top-0 z-20">
          <DashboardSection gridCols={1} className="py-6">
            <div className="flex flex-col gap-4">
              {breadcrumbs && (
                <div className="flex items-center text-[10px] font-bold text-slate-400 uppercase tracking-[0.2em] mb-1">
                  {breadcrumbs}
                </div>
              )}
              <div className="flex flex-wrap justify-between items-center gap-4">
                <div>
                  <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight leading-tight">
                    {title}
                  </h2>
                  <p className="text-muted-foreground mt-1 text-sm font-medium">
                    {description}
                  </p>
                </div>
                {headerActions && <div className="flex gap-3">{headerActions}</div>}
              </div>
            </div>

            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-8">
                {stats}
              </div>
            )}

            {filters && <div className="mt-8">{filters}</div>}
          </DashboardSection>
        </header>

        <div className="bg-slate-50/50 dark:bg-slate-900/50 min-h-full pb-20">
          <DashboardSection gridCols={1} className="py-8">
            {children}
          </DashboardSection>
        </div>
      </main>
    </div>
  );
}
