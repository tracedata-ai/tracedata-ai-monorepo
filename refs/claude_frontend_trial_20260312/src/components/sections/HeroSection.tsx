import { landingConfig } from "@/config/landing";
import { Play } from "lucide-react";
import { LandingBadge } from "../landing/LandingBadge";
import { HeroButton } from "../landing/HeroButton";
import { PremiumCard } from "../landing/PremiumCard";

export function HeroSection() {
  const { hero } = landingConfig;
  
  return (
    <section className="relative min-h-[95vh] flex items-center pt-24 overflow-hidden" id="hero">
      {/* Background Layer with Sophisticated Lighting */}
      <div className="absolute inset-0 -z-20 scale-105">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src="/images/hero-bg.png" 
          alt={hero.visualAlt}
          className="w-full h-full object-cover opacity-60 dark:opacity-40 grayscale-[20%]"
        />
        <div className="absolute inset-0 bg-background/40 dark:bg-[#090e1a]/80 backdrop-blur-[2px]"></div>
        <div className="absolute inset-0 bg-gradient-to-tr from-background dark:from-[#090e1a] via-transparent to-brand-teal/5"></div>
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-background dark:to-[#090e1a]"></div>
      </div>
      
      <div className="absolute inset-0 grid-overlay opacity-[0.03] dark:opacity-[0.07] -z-10"></div>
      
      <div className="container mx-auto px-6 grid lg:grid-cols-12 gap-16 items-center relative z-10">
        <div className="lg:col-span-7 max-w-3xl">
          <LandingBadge text="Transparency Protocol v4.0 Active" className="mb-8" />
          
          <h1 className="text-7xl md:text-[7.5rem] font-black mb-8 leading-[0.85] tracking-[-0.04em] text-foreground dark:text-white text-balance">
            {hero.title.prefix}
            <span className="block text-transparent bg-clip-text bg-gradient-to-br from-brand-teal via-brand-blue to-brand-teal animate-gradient-x">
              {hero.title.highlight}
            </span>
          </h1>
          
          <p className="text-2xl text-foreground/80 dark:text-white/60 mb-12 max-w-xl leading-relaxed font-medium tracking-tight">
            {hero.description}
          </p>
          
          <div className="flex flex-wrap gap-6 items-center">
            <HeroButton variant="primary">
              {hero.primaryCta}
              <div className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center -mr-1">
                <div className="w-1.5 h-1.5 border-t-2 border-r-2 border-white rotate-45 -ml-0.5"></div>
              </div>
            </HeroButton>
            <HeroButton variant="secondary" className="group">
              <div className="w-10 h-10 rounded-full bg-brand-teal/10 dark:bg-white/10 flex items-center justify-center text-brand-teal dark:text-white group-hover:scale-110 transition-transform shadow-inner">
                <Play size={16} fill="currentColor" />
              </div>
              {hero.secondaryCta}
            </HeroButton>
          </div>
        </div>
        
        <div className="lg:col-span-5 relative lg:block hidden">
          <PremiumCard className="p-12 rounded-[3rem]" hoverEffect={false}>
            <div className="absolute top-0 right-0 w-80 h-80 bg-brand-teal/10 blur-[100px] -z-10"></div>
            
            <div className="space-y-12 relative">
              <div className="relative">
                <header className="flex justify-between items-center mb-4">
                  <span className="text-[10px] text-brand-teal font-black uppercase tracking-[0.2em] opacity-80">
                    Confidence Index
                  </span>
                  <div className="flex gap-1">
                    <div className="w-1 h-3 bg-brand-teal/20 rounded-full"></div>
                    <div className="w-1 h-3 bg-brand-teal rounded-full"></div>
                  </div>
                </header>
                <div className="flex items-baseline gap-3">
                  <span className="text-8xl font-black text-foreground dark:text-white tracking-tighter leading-none">
                    {hero.metrics.driverSatisfaction.value}
                  </span>
                  <span className="text-brand-teal text-2xl font-black">{hero.metrics.driverSatisfaction.unit}</span>
                </div>
                <p className="text-sm text-muted-foreground dark:text-white/40 font-bold mt-4 uppercase tracking-widest">Global Driver Trust Rating</p>
              </div>
              
              <div className="h-px bg-black/[0.03] dark:bg-white/[0.03] w-full"></div>
              
              <div className="grid grid-cols-2 gap-12">
                <div>
                  <span className="text-[10px] text-brand-blue font-black uppercase tracking-[0.2em] mb-2 block opacity-80">
                    Audit Frequency
                  </span>
                  <span className="text-4xl font-bold text-foreground dark:text-white tracking-tight">
                    {hero.metrics.dataClarity.value}
                  </span>
                  <span className="text-xs text-brand-blue font-black ml-1">Hz</span>
                </div>
                <div className="flex items-end justify-end">
                   <div className="flex gap-1.5 items-end h-16 group/bars">
                    {[0.4, 0.7, 1.0, 0.6, 0.9, 0.5].map((h, i) => (
                      <div 
                        key={i} 
                        className="w-2 rounded-full transition-all duration-500 bg-brand-teal/20 dark:bg-white/10"
                        style={{ height: `${h * 100}%` }}
                      >
                         <div 
                          className="w-full h-full bg-gradient-to-t from-brand-teal to-brand-blue rounded-full opacity-60"
                          style={{ height: `${(i % 2 === 0 ? 0.8 : 0.4) * 100}%` }}
                        ></div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </PremiumCard>
          
          <div className="absolute -bottom-10 -left-10 glass-card p-6 rounded-[2rem] border border-black/5 dark:border-white/10 shadow-2xl animate-bounce-slow flex items-center gap-5 hover:scale-105 transition-transform cursor-pointer">
             <div className="w-14 h-14 rounded-2xl bg-brand-teal/10 flex items-center justify-center shadow-inner group">
               <div className="w-3 h-3 rounded-full bg-brand-teal animate-ping"></div>
             </div>
             <div>
               <p className="text-[10px] font-black text-foreground dark:text-white uppercase tracking-[0.2em] mb-1">Network Status</p>
               <p className="text-sm font-black text-brand-teal uppercase tracking-tight">Optimal Equilibrium</p>
             </div>
          </div>
        </div>
      </div>
    </section>
  );
}
