import React from "react";

interface PremiumCardProps {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}

export function PremiumCard({ children, className = "", hoverEffect = true }: PremiumCardProps) {
  return (
    <div className={`
      glass-card border border-black/10 dark:border-white/[0.03] shadow-sm
      ${hoverEffect ? 'hover:border-brand-teal/30 dark:hover:border-brand-teal/30 transition-all duration-700 hover:-translate-y-3 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.15)] dark:hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.4)]' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
}
