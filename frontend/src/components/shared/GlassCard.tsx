import * as React from "react"
import { cn } from "@/lib/utils"

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  variant?: "default" | "brand"
}

export function GlassCard({ className, children, variant = "default", ...props }: GlassCardProps) {
  return (
    <div
      className={cn(
        "p-6 sm:p-8 rounded-[2rem] transition-all duration-500 relative overflow-hidden",
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
    </div>
  )
}
