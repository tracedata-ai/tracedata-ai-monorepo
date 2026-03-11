import { landingConfig } from "@/config/landing";
import * as LucideIcons from "lucide-react";
import { SectionHeader } from "../landing/SectionHeader";
import { PremiumCard } from "../landing/PremiumCard";
import { SectionWrapper } from "../landing/SectionWrapper";

export function SolutionGrid() {
  const { solutions } = landingConfig;
  
  return (
    <SectionWrapper id="solutions">
      <SectionHeader 
        badge={solutions.badge}
        title={solutions.title}
        align="left"
      />
      
      <div className="grid md:grid-cols-3 gap-10">
        {solutions.items.map((item, i) => {
          const Icon = item.icon;
          return (
            <PremiumCard key={i} className="p-10 rounded-[2.5rem]">
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
            </PremiumCard>
          );
        })}
      </div>
    </SectionWrapper>
  );
}
