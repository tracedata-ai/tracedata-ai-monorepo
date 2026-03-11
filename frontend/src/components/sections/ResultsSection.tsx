import { landingConfig } from "@/config/landing";
import { SectionHeader } from "../landing/SectionHeader";
import { SectionWrapper } from "../landing/SectionWrapper";

export function ResultsSection() {
  const { stats } = landingConfig;
  
  return (
    <SectionWrapper id="results" darkBg>
      <SectionHeader 
        title={stats.title}
        description="Measurable impact across the global logistics chain."
        align="left"
      />
      
      <div className="grid md:grid-cols-3 gap-16 lg:gap-24">
        {stats.items.map((stat, i) => (
          <div key={i} className="relative group">
            <div className="relative">
              <div className="text-8xl lg:text-[10rem] font-black mb-4 font-mono text-foreground dark:text-white tracking-tighter leading-none group-hover:text-brand-teal transition-colors duration-500">
                {stat.value}
              </div>
              <div className="text-[10px] text-muted-foreground dark:text-white/30 font-black uppercase tracking-[0.3em]">
                {stat.label}
              </div>
            </div>
            
            <div className="mt-8 h-1 w-full bg-black/5 dark:bg-white/5 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-brand-teal to-brand-blue transition-all duration-1000 w-[60%] group-hover:w-full"
              ></div>
            </div>
          </div>
        ))}
      </div>
{/* 
      Join the Network section - simplified but premium */}
      <div className="mt-32 pt-20 border-t border-black/[0.03] dark:border-white/[0.03] flex flex-col lg:flex-row items-center justify-between gap-12">
        <div className="flex items-center gap-8">
           <div className="flex -space-x-5">
              {[1,2,3,4,5].map(i => (
                <div key={i} className="w-16 h-16 rounded-full border-[4px] border-brand-surface dark:border-[#0b1222] bg-muted dark:bg-[#1e293b] flex items-center justify-center text-xs font-black text-brand-teal shadow-2xl transition-transform hover:-translate-y-2 hover:z-20">
                  {String.fromCharCode(64 + i)}
                </div>
              ))}
            </div>
            <div className="max-w-[200px]">
              <p className="text-lg font-black text-foreground dark:text-white tracking-tight leading-tight">Join the Network</p>
              <p className="text-xs text-muted-foreground dark:text-white/30 font-bold mt-1">Over 12,000 operators connected daily.</p>
            </div>
        </div>
        <button className="h-20 px-12 glass-card hover:bg-black/5 dark:hover:bg-white/5 transition-all font-black rounded-3xl border border-black/5 dark:border-white/10 text-xs uppercase tracking-[0.2em] shadow-premium group">
          <span className="group-hover:tracking-[0.3em] transition-all">Read Success Stories</span>
        </button>
      </div>
    </SectionWrapper>
  );
}
