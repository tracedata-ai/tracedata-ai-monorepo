import * as React from "react"
import { cn } from "@/lib/utils"
import { GlassCard } from "./GlassCard"
import { LucideIcon } from "lucide-react"

interface FeatureCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  subtitle?: string
  icon: LucideIcon
  actions?: React.ReactNode
  variant?: "default" | "brand"
  isNarrative?: boolean
}

export function FeatureCard({
  title,
  subtitle,
  icon: Icon,
  actions,
  variant = "default",
  isNarrative = false,
  className,
  children,
  ...props
}: FeatureCardProps) {
  return (
    <GlassCard variant={variant} className={cn("flex flex-col h-full", className)} {...props}>
      {/* Universal Header Motif */}
      <div className="flex justify-between items-start mb-8 relative z-10">
        <div className="flex items-center gap-4">
          <div className={cn(
            "p-2 rounded-xl border flex items-center justify-center text-slate-900",
            variant === "brand" ? "bg-white border-brand-blue/10" : "bg-slate-50 border-slate-100"
          )}>
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2">
              {title}
            </h3>
            {subtitle && (
              <p className="text-sm font-bold text-slate-600 mt-0.5">{subtitle}</p>
            )}
          </div>
        </div>
        
        {actions && (
          <div className="flex items-center gap-2">
            {actions}
          </div>
        )}
      </div>

      <div className={cn(
        "relative flex-1",
        isNarrative && "bg-slate-50/50 border border-slate-100 p-8 rounded-3xl"
      )}>
        {isNarrative && (
          <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-4">
            AI Narrative Analysis
          </p>
        )}
        <div className={cn(isNarrative && "text-xl font-bold text-slate-900 leading-tight italic")}>
          {children}
        </div>
      </div>
    </GlassCard>
  )
}
