import React from "react";

interface SectionWrapperProps {
  id?: string;
  children: React.ReactNode;
  className?: string;
  variant?: "light" | "surface" | "navy";
}

export function SectionWrapper({ id, children, className = "", variant = "light" }: SectionWrapperProps) {
  const bgClasses = {
    light: "bg-[#f0f9ff] text-[#0f172a] [--muted-foreground:oklch(0.35_0_0)]",
    surface: "bg-[#e0f2fe] text-[#0f172a] [--muted-foreground:oklch(0.35_0_0)]",
    navy: "bg-[#0f172a] text-white [--muted-foreground:rgba(255,255,255,0.6)] border-t border-white/[0.03]",
  };
  
  return (
    <section 
      id={id} 
      className={`section-padding relative overflow-hidden transition-colors duration-500 ${bgClasses[variant]} ${className}`}
      style={{
        // @ts-expect-error - Setting custom property for children
        "--section-variant": variant 
      }}
    >
      <div className="container mx-auto px-6 relative z-10">
        {children}
      </div>
      
      {/* Dynamic Grid Overlay */}
      <div className={`absolute inset-0 grid-overlay ${variant === 'navy' ? 'opacity-[0.05]' : 'opacity-[0.03] dark:opacity-[0.07]'} pointer-events-none`}></div>

      {/* Standardized decorative glows */}
      <div className={`absolute top-1/2 left-0 -translate-y-1/2 w-96 h-96 blur-[120px] -z-10 rounded-full pointer-events-none ${variant === 'navy' ? 'bg-brand-teal/10' : 'bg-brand-teal/5'}`}></div>
      <div className={`absolute bottom-0 right-0 w-96 h-96 blur-[120px] -z-10 rounded-full pointer-events-none ${variant === 'navy' ? 'bg-brand-blue/10' : 'bg-brand-blue/5'}`}></div>
    </section>
  );
}
