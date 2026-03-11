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
        
        <div className="grid md:grid-cols-3 gap-8">
          {solutions.items.map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} className="group p-8 rounded-3xl bg-white dark:bg-muted/30 border border-black/5 dark:border-border hover:border-brand-teal/50 transition-all duration-300 hover:shadow-2xl hover:shadow-brand-teal/5">
                <div className={`w-14 h-14 rounded-2xl bg-muted/50 dark:bg-background border border-black/5 dark:border-border flex items-center justify-center mb-8 group-hover:scale-110 group-hover:bg-brand-teal/10 group-hover:border-brand-teal/20 transition-all text-brand-teal`}>
                  <Icon size={28} />
                </div>
                <h4 className="text-xl font-bold mb-4 text-foreground group-hover:text-brand-teal transition-colors">
                  {item.title}
                </h4>
                <p className="text-muted-foreground dark:text-gray-400 leading-relaxed font-medium">
                  {item.description}
                </p>
                <div className="mt-8 flex items-center gap-2 text-xs font-black text-foreground opacity-0 group-hover:opacity-100 transition-all translate-x-[-10px] group-hover:translate-x-0 tracking-widest">
                  LEARN MORE 
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
