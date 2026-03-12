import * as React from "react"
import { cn } from "@/lib/utils"
import { Card } from "@/components/ui/card"

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  variant?: "default" | "brand"
  compact?: boolean
}

export function GlassCard({ className, children, variant = "default", compact = false, ...props }: GlassCardProps) {
  return (
    <Card
      className={cn(
        "transition-all duration-500 relative overflow-hidden border-0 shadow-none ring-0",
        compact ? "p-5 rounded-3xl" : "p-6 sm:p-8 rounded-[2rem]",
        "bg-white border border-slate-200/60 shadow-[0_8px_30px_rgb(0,0,0,0.02)]",
        "hover:shadow-[0_20px_40px_rgba(0,0,0,0.04)] hover:-translate-y-1",
        variant === "brand" && "bg-gradient-to-br from-white to-brand-blue/[0.02] border-brand-blue/10",
        className
      )}
      {...props}
    >
      <div className="relative z-10">
        {children}
      </div>
    </Card>
  )
}
