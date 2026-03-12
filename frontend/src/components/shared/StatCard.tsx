import * as React from "react";
import { LucideIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * StatCard Props
 */
interface StatCardProps {
  /** The title of the metric */
  title: string;
  /** The primary value to display */
  value: string | number;
  /** Optional icon component from lucide-react */
  icon?: LucideIcon;
  /** Optional secondary description/subtext */
  description?: string;
  /** Custom class for the outer card container */
  className?: string;
  /** Custom class for the icon element */
  iconClassName?: string;
  /** Custom class for the value text */
  valueClassName?: string;
}

/**
 * StatCard Component
 *
 * A reusable dashboard metric card that standardizes the presentation
 * of analytics and status indicators across the platform.
 */
export function StatCard({
  title,
  value,
  icon: Icon,
  description,
  className,
  iconClassName,
  valueClassName,
}: StatCardProps) {
  return (
    <Card className={cn("border shadow-none transition-all", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 p-4 pb-2">
        <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
          {Icon && <Icon className={cn("w-4 h-4", iconClassName)} />}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <div
          className={cn("text-2xl font-bold text-slate-900", valueClassName)}
        >
          {value}
        </div>
        {description && (
          <p className="text-[10px] text-slate-500 mt-1 font-medium">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
