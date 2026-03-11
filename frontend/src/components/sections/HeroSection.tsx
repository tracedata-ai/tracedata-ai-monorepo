import { landingConfig } from "@/config/landing";

export function HeroSection() {
  const { hero } = landingConfig;
  
  return (
    <section className="relative min-h-[90vh] flex items-center pt-20 overflow-hidden" data-purpose="hero-section" id="hero">
      {/* Background Image with Adaptive Overlay */}
      <div className="absolute inset-0 -z-20">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src="/images/hero-bg.png" 
          alt={hero.visualAlt}
          className="w-full h-full object-cover"
        />
        {/* Adaptive Overlay using CSS Variable */}
        <div className="absolute inset-0 bg-brand-surface/60 dark:bg-brand-deep-navy/80 transition-colors"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-brand-surface/30 dark:via-brand-deep-navy/30 to-brand-surface dark:to-brand-deep-navy"></div>
      </div>
      
      <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center relative z-10 py-12 lg:py-24">
        <div data-purpose="hero-content" className="max-w-2xl">
          <div className="mb-6 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-teal/10 border border-brand-teal/20 backdrop-blur-md">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-teal opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-teal"></span>
            </span>
            <span className="text-[10px] font-bold text-brand-teal uppercase tracking-widest">
              Live Transparency Protocol Active
            </span>
          </div>
          
          <h1 className="text-6xl md:text-8xl font-black mb-6 leading-[0.9] text-foreground dark:text-white tracking-tighter text-balance">
            {hero.title.prefix}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-teal to-brand-blue">
              {hero.title.highlight}
            </span>
          </h1>
          
          <p className="text-xl text-muted-foreground dark:text-gray-300 mb-10 max-w-xl leading-relaxed font-medium">
            {hero.description}
          </p>
          
          <div className="flex flex-wrap gap-4">
            <button className="px-10 py-5 bg-brand-teal text-white font-bold rounded-xl hover:bg-brand-teal/90 transition-all shadow-lg shadow-brand-teal/20 hover:scale-[1.02] active:scale-[0.98]">
              {hero.primaryCta}
            </button>
            <button className="px-10 py-5 glass-card text-foreground dark:text-white hover:bg-black/5 dark:hover:bg-white/10 rounded-xl transition-all font-bold flex items-center gap-3 shadow-sm">
              <div className="w-8 h-8 rounded-full bg-black/5 dark:bg-white/10 flex items-center justify-center">
                <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-current border-b-[6px] border-b-transparent ml-1"></div>
              </div>
              {hero.secondaryCta}
            </button>
          </div>
        </div>
        
        {/* Hero Visual - Premium Stats Card */}
        <div className="relative lg:block hidden" data-purpose="hero-visual">
          <div className="glass-card p-10 rounded-3xl border border-black/5 dark:border-white/10 relative overflow-hidden group shadow-xl">
            <div className="absolute top-0 right-0 w-64 h-64 bg-brand-teal/10 blur-[80px] -z-10 group-hover:bg-brand-teal/20 transition-colors"></div>
            
            <div className="space-y-8">
              <div>
                <span className="text-[10px] text-brand-teal font-bold uppercase tracking-widest mb-2 block">
                  Dashboard Performance
                </span>
                <div className="flex items-baseline gap-2">
                  <span className="text-6xl font-black text-foreground dark:text-white font-mono">
                    {hero.metrics.driverSatisfaction.value}
                  </span>
                  <span className="text-brand-teal text-xl font-bold">{hero.metrics.driverSatisfaction.unit}</span>
                </div>
                <p className="text-sm text-muted-foreground dark:text-gray-400 mt-1">Driver Transparency Rating</p>
              </div>
              
              <div className="h-px bg-black/5 dark:bg-white/5 w-full"></div>
              
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <span className="text-[10px] text-brand-blue font-bold uppercase tracking-widest mb-1 block">
                    Data Integrity
                  </span>
                  <span className="text-3xl font-mono text-foreground dark:text-white">
                    {hero.metrics.dataClarity.value}
                  </span>
                </div>
                <div className="flex items-end justify-end">
                   <div className="flex gap-1 items-end h-16">
                    <div className="w-1.5 bg-brand-teal h-[40%] animate-pulse"></div>
                    <div className="w-1.5 bg-brand-blue h-[70%] animate-pulse delay-75"></div>
                    <div className="w-1.5 bg-brand-teal h-[100%] animate-pulse delay-150"></div>
                    <div className="w-1.5 bg-brand-blue h-[60%] animate-pulse delay-300"></div>
                    <div className="w-1.5 bg-brand-teal h-[80%] animate-pulse delay-500"></div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-8 pt-8 border-t border-black/5 dark:border-white/5 flex items-center gap-4">
              <div className="flex -space-x-3">
                {[1,2,3,4].map(i => (
                  <div key={i} className="w-8 h-8 rounded-full border-2 border-background dark:border-brand-deep-navy bg-muted dark:bg-brand-slate flex items-center justify-center text-[10px] font-bold text-foreground dark:text-white">
                    D{i}
                  </div>
                ))}
              </div>
              <span className="text-xs text-muted-foreground dark:text-gray-400">Trusted by over 4,000 drivers worldwide</span>
            </div>
          </div>
          
          {/* Floating Element */}
          <div className="absolute -bottom-6 -left-6 glass-card p-4 rounded-2xl border border-black/5 dark:border-white/10 shadow-2xl animate-bounce-slow">
             <div className="flex items-center gap-3">
               <div className="w-10 h-10 rounded-lg bg-brand-teal/20 flex items-center justify-center">
                 <div className="w-2 h-2 rounded-full bg-brand-teal animate-ping"></div>
               </div>
               <div>
                 <p className="text-[10px] font-bold text-foreground dark:text-white uppercase tracking-wider">System Status</p>
                 <p className="text-[10px] text-brand-teal font-bold uppercase">Optimal Equilibrium</p>
               </div>
             </div>
          </div>
        </div>
      </div>
    </section>
  );
}
