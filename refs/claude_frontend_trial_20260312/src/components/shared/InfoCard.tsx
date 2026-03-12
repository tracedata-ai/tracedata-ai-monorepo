import * as React from "react"
import { cn } from "@/lib/utils"
import { GlassCard } from "./GlassCard"
import { LucideIcon } from "lucide-react"

interface InfoItem {
  label: string
  value: React.ReactNode
  icon?: LucideIcon
  className?: string
}

interface InfoCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  icon?: LucideIcon
  items?: InfoItem[]
  columns?: 1 | 2
  variant?: "default" | "brand"
  children?: React.ReactNode
}

export function InfoCard({
  title,
  icon: TitleIcon,
  items = [],
  columns = 2,
  variant = "default",
  className,
  children,
  ...props
}: InfoCardProps) {
  return (
    <GlassCard variant={variant} className={cn("flex flex-col h-full", className)} {...props}>
      {title && (
        <div className="mb-6 flex items-center gap-2">
          {TitleIcon && <TitleIcon className="w-4 h-4 text-brand-blue" />}
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">
            {title}
          </h3>
        </div>
      )}
      
      <div className={cn(
        "grid gap-6",
        columns === 2 ? "grid-cols-2" : "grid-cols-1"
      )}>
        {items.map((item, index) => (
          <div key={index} className={cn("flex flex-col", item.className)}>
            <div className="flex items-center gap-1.5 mb-1.5">
              {item.icon && <item.icon className="w-3.5 h-3.5 text-slate-400" />}
              <span className="text-xs font-bold text-slate-500 uppercase tracking-tight">
                {item.label}
              </span>
            </div>
            <div className="text-sm font-bold text-slate-900 leading-tight">
              {item.value || "--"}
            </div>
          </div>
        ))}
      </div>
      {children}
    </GlassCard>
  )
}
