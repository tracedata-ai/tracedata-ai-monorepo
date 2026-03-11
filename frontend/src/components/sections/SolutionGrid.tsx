import { landingConfig } from "@/config/landing";
import * as LucideIcons from "lucide-react";

export function SolutionGrid() {
  const { solutions } = landingConfig;
  
  return (
    <section className="section-padding bg-background relative overflow-hidden" id="solutions">
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>
      
      <div className="container mx-auto px-6">
        <div className="max-w-3xl mb-16">
          <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
            {solutions.badge}
          </h2>
          <h3 className="text-4xl md:text-5xl font-black mb-6 text-foreground tracking-tighter text-balance">
            {solutions.title}
          </h3>
        </div>
        
        <div className="grid md:grid-cols-3 gap-10">
          {solutions.items.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="group p-10 rounded-[2.5rem] bg-white dark:bg-muted/10 border border-black/[0.03] dark:border-white/[0.03] glass-card hover:border-brand-teal/30 dark:hover:border-brand-teal/30 transition-all duration-500 hover:-translate-y-2 hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.1)] dark:hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.4)]">
                <div className="w-16 h-16 rounded-2xl bg-brand-teal/10 dark:bg-brand-teal/5 flex items-center justify-center mb-10 group-hover:scale-110 group-hover:rotate-3 transition-all duration-500 shadow-inner text-brand-teal relative">
                  <Icon size={32} strokeWidth={1.5} />
                  <div className="absolute inset-0 bg-brand-teal/20 blur-xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </div>
                <h4 className="text-2xl font-black mb-5 text-foreground dark:text-white tracking-tight group-hover:text-brand-teal transition-colors duration-300">
                  {item.title}
                </h4>
                <p className="text-lg text-muted-foreground dark:text-white/40 leading-relaxed font-medium tracking-tight">
                  {item.description}
                </p>
                <div className="mt-10 flex items-center gap-3 text-[10px] font-black text-foreground dark:text-white opacity-40 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0 tracking-[0.2em] uppercase">
                  Explore Architecture 
                  <LucideIcons.ArrowRight size={14} className="text-brand-teal" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
      
      {/* Decorative Background Element */}
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-blue/5 blur-[100px] -z-10 rounded-full"></div>
    </section>
  );
}
