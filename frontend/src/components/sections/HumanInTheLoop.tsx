import React from "react";
import { landingConfig } from "@/config/landing";

export function HumanInTheLoop() {
  const { humanInTheLoop } = landingConfig;
  
  return (
    <section className="py-24 bg-card relative overflow-hidden" data-purpose="human-in-the-loop">
      {/* Dynamic Background */}
      <div className="absolute inset-0 bg-[image:var(--background-image-mission-control)] opacity-5 dark:opacity-100 mix-blend-multiply dark:mix-blend-normal pointer-events-none transition-opacity"></div>
      
      <div className="container mx-auto px-6 text-center relative pointer-events-auto">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
            {humanInTheLoop.subheading}
          </h2>
          <h3 className="text-4xl md:text-5xl font-bold mb-8 fragmented-header text-foreground">
            {humanInTheLoop.title}
          </h3>
          <p className="text-xl text-muted-foreground mb-12">
            {humanInTheLoop.description}
          </p>
          
          <div className="inline-flex flex-col md:flex-row gap-8 items-center bg-background/80 p-8 rounded-3xl border border-border shadow-lg backdrop-blur-xl">
            {humanInTheLoop.metrics.map((metric, i) => (
              <React.Fragment key={i}>
                {i > 0 && <div className="w-12 h-px md:w-px md:h-12 bg-border"></div>}
                <div className="text-center md:text-left">
                  <span className={`block text-4xl font-bold text-${metric.color}`}>{metric.value}</span>
                  <span className="text-xs uppercase tracking-widest text-muted-foreground">{metric.label}</span>
                </div>
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
