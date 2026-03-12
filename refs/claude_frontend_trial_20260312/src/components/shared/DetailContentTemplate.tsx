"use client";

import React from "react";
import { DashboardSection } from "./DashboardSection";
import { MetricCard } from "./MetricCard";
import { cn } from "@/lib/utils";
import { Separator } from "@/components/ui/separator";
import { LucideIcon } from "lucide-react";

interface DetailContentTemplateProps {
  heroIcon: LucideIcon;
  heroTitle: string;
  heroSubtitle: string;
  highlights: {
    label: string;
    value: string | number;
    icon?: LucideIcon;
    className?: string;
    iconColor?: string;
  }[];
  children: React.ReactNode;
}

export function DetailContentTemplate({
  heroIcon: HeroIcon,
  heroTitle,
  heroSubtitle,
  highlights,
  children,
}: DetailContentTemplateProps) {
  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-6 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm">
            <HeroIcon className="w-6 h-6" />
          </div>
          <div>
            <h4 className="text-xl font-black text-foreground tracking-tight leading-tight uppercase font-mono">
              {heroTitle}
            </h4>
            <p className="text-[10px] text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">
              {heroSubtitle}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {highlights.map((h, i) => (
            <MetricCard
              key={i}
              compact
              label={h.label}
              value={h.value}
              icon={h.icon}
              className={h.className}
              iconColor={h.iconColor}
            />
          ))}
        </div>
      </DashboardSection>

      <div className="p-6 space-y-6 overflow-y-auto">
        {children}
      </div>
    </div>
  );
}
