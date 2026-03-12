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
}

export function MetricCard({
  label,
  value,
  subValue,
  icon: Icon,
  iconColor = "text-brand-blue",
  trend,
  className,
  children,
  ...props
}: MetricCardProps) {
  return (
    <GlassCard className={cn("flex flex-col h-full group hover:shadow-[0_20px_40px_rgba(0,0,0,0.06)]", className)} {...props}>
      <div className="flex justify-between items-start mb-6">
        <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          {label}
        </h3>
        {Icon && (
          <div className={cn("p-2.5 bg-slate-50 rounded-2xl border border-slate-100 group-hover:scale-110 transition-transform duration-500", iconColor)}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex flex-col flex-1 justify-center">
        <p className="text-4xl font-black text-slate-900 leading-none mb-3 font-mono tracking-tighter">
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
