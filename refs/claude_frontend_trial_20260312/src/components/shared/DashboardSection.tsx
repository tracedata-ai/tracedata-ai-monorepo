import * as React from "react"
import { cn } from "@/lib/utils"

interface DashboardSectionProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string
  description?: string
  isFullWidth?: boolean
  gridCols?: 1 | 2 | 3 | 4
}

export function DashboardSection({
  title,
  description,
  isFullWidth = false,
  gridCols = 3,
  className,
  children,
  ...props
}: DashboardSectionProps) {
  return (
    <section 
      className={cn(
        "w-full px-4 sm:px-8 py-6", 
        !isFullWidth && "max-w-7xl mx-auto",
        className
      )} 
      {...props}
    >
      {(title || description) && (
        <div className="mb-8">
          {title && (
            <h2 className="text-xl font-black text-slate-900 tracking-tight">
              {title}
            </h2>
          )}
          {description && (
            <p className="text-sm font-medium text-slate-500 mt-1">
              {description}
            </p>
          )}
        </div>
      )}
      
      <div className={cn(
        "grid gap-6",
        gridCols === 1 && "grid-cols-1",
        gridCols === 2 && "grid-cols-1 md:grid-cols-2",
        gridCols === 3 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        gridCols === 4 && "grid-cols-1 md:grid-cols-2 lg:grid-cols-4"
      )}>
        {children}
      </div>
    </section>
  )
}
