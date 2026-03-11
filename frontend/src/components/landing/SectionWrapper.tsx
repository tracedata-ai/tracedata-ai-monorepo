import React from "react";

interface SectionWrapperProps {
  id?: string;
  children: React.ReactNode;
  className?: string;
  darkBg?: boolean;
}

export function SectionWrapper({ id, children, className = "", darkBg = false }: SectionWrapperProps) {
  const bgClass = darkBg ? "bg-brand-surface dark:bg-[#0b1222]" : "bg-background";
  
  return (
    <section 
      id={id} 
      className={`section-padding relative overflow-hidden ${bgClass} ${className}`}
    >
      <div className="container mx-auto px-6 relative z-10">
        {children}
      </div>
      
      {/* Dynamic Grid Overlay - only shown in sections that aren't the hero (which has its own) or as needed */}
      <div className="absolute inset-0 grid-overlay opacity-[0.03] dark:opacity-[0.07] pointer-events-none"></div>

      {/* Standardized decorative glows */}
      <div className="absolute top-1/2 left-0 -translate-y-1/2 w-96 h-96 bg-brand-teal/5 dark:bg-brand-teal/5 blur-[120px] -z-10 rounded-full pointer-events-none"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-blue/5 dark:bg-brand-blue/5 blur-[120px] -z-10 rounded-full pointer-events-none"></div>
    </section>
  );
}
