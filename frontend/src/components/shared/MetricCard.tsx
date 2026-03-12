import * as React from "react"
import { cn } from "@/lib/utils"
import { GlassCard } from "./GlassCard"
import { LucideIcon } from "lucide-react"

interface MetricCardProps extends React.HTMLAttributes<HTMLDivElement> {
  label: string
  value: string | number
  subValue?: string
  icon?: LucideIcon
  iconColor?: string
  trend?: {
    value: number
    label: string
    isPositive?: boolean
  }
  compact?: boolean
}

export function MetricCard({
  label,
  value,
  subValue,
  icon: Icon,
  iconColor = "text-brand-blue",
  trend,
  compact,
  className,
  children,
  ...props
}: MetricCardProps) {
  return (
    <GlassCard compact={compact} className={cn("flex flex-col h-full group hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)]", className)} {...props}>
      <div className={cn("flex justify-between items-start", compact ? "mb-2 min-h-[32px]" : "mb-6 min-h-[44px]")}>
        <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          {label}
        </h3>
        {Icon && (
          <div className={cn(
            "rounded-2xl border border-slate-100 group-hover:scale-110 transition-transform duration-500",
            compact ? "p-1.5" : "p-2.5 bg-slate-50",
            iconColor
          )}>
            <Icon className={cn(compact ? "w-3.5 h-3.5" : "w-4 h-4")} />
          </div>
        )}
      </div>

      <div className="flex flex-col flex-1 justify-center">
        <p className={cn(
          "font-black text-slate-900 leading-none font-mono tracking-tighter",
          compact ? "text-2xl mb-1" : "text-4xl mb-3"
        )}>
          {value}
        </p>
        {(subValue || trend) && (
          <div className="flex items-center gap-3">
            {subValue && (
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tighter">
                {subValue}
              </p>
            )}
            {trend && (
              <span className={cn(
                "text-[10px] font-black px-2.5 py-1 rounded-full border shadow-sm",
                trend.isPositive 
                  ? "bg-emerald-50 text-emerald-600 border-emerald-100" 
                  : "bg-rose-50 text-rose-600 border-rose-100"
              )}>
                {trend.isPositive ? '+' : '-'}{trend.value}% {trend.label}
              </span>
            )}
          </div>
        )}
      </div>

      {children && (
        <div className="mt-6 pt-6 border-t border-slate-100/50">
          {children}
        </div>
      )}
    </GlassCard>
  )
}
