import Image from "next/image";
import { landingConfig } from "@/config/landing";

export function HeroSection() {
  const { hero } = landingConfig;
  
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden" data-purpose="hero-section" id="hero">
      <div className="absolute inset-0 grid-overlay opacity-30 dark:opacity-100 -z-10"></div>
      <div className="absolute top-1/4 -right-20 w-96 h-96 bg-brand-teal/10 dark:bg-brand-teal/20 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-1/4 -left-20 w-96 h-96 bg-brand-blue/10 dark:bg-brand-blue/20 blur-[120px] rounded-full"></div>
      
      <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
        <div data-purpose="hero-content">
          <h1 className="text-6xl md:text-7xl font-extrabold mb-6 leading-tight fragmented-header text-foreground">
            {hero.title.prefix}
            <span className="text-transparent bg-clip-text bg-[image:var(--background-image-gradient-brand)]">
              {hero.title.highlight}
            </span>{" "}
            {hero.title.suffix}
          </h1>
          <p className="text-xl text-muted-foreground mb-10 max-w-xl leading-relaxed">
            {hero.description}
          </p>
          
          <div className="flex flex-wrap gap-4">
            <button className="px-8 py-4 bg-foreground text-background font-bold rounded-lg hover:opacity-90 transition-colors">
              {hero.primaryCta}
            </button>
            <button className="px-8 py-4 border border-border text-foreground hover:bg-muted rounded-lg transition-colors font-semibold">
              {hero.secondaryCta}
            </button>
          </div>
          
          {/* XAI Metrics Small Card */}
          <div className="mt-12 p-4 bg-background/50 border border-border rounded-xl backdrop-blur-sm flex items-center gap-6 max-w-md shadow-sm">
            <div className="flex flex-col">
              <span className="text-[10px] text-brand-teal font-bold uppercase tracking-widest">
                {hero.metrics.activeOrchestration.label}
              </span>
              <span className="text-2xl font-mono text-foreground">
                {hero.metrics.activeOrchestration.value}<span className="text-brand-blue text-sm">{hero.metrics.activeOrchestration.unit}</span>
              </span>
            </div>
            <div className="h-10 w-px bg-border"></div>
            <div className="flex flex-col">
              <span className="text-[10px] text-brand-blue font-bold uppercase tracking-widest">
                {hero.metrics.latency.label}
              </span>
              <span className="text-2xl font-mono text-foreground">
                {hero.metrics.latency.value}<span className="text-brand-teal text-sm">{hero.metrics.latency.unit}</span>
              </span>
            </div>
            <div className="h-10 w-px bg-border"></div>
            <div className="flex-grow flex justify-end">
              <div className="flex gap-1 items-end h-8">
                <div className="w-1 bg-brand-teal h-4"></div>
                <div className="w-1 bg-brand-blue h-6"></div>
                <div className="w-1 bg-brand-teal h-8"></div>
                <div className="w-1 bg-brand-blue h-5"></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Hero Visual */}
        <div className="relative group" data-purpose="hero-visual">
          <div className="absolute -inset-4 bg-[image:var(--background-image-gradient-brand)] opacity-10 dark:opacity-20 blur-xl group-hover:opacity-20 dark:group-hover:opacity-30 transition-opacity"></div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            alt={hero.visualAlt}
            className="relative rounded-2xl border border-border shadow-2xl w-full object-cover"
            src={hero.visualSrc}
          />
        </div>
      </div>
    </section>
  );
}
