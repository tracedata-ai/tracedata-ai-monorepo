"use client";

import { landingConfig } from "@/config/landing";

export function LogoMarquee() {
  const { trustedBy } = landingConfig;
  
  // Double the logos for seamless loop
  const logos = [...trustedBy, ...trustedBy];

  return (
    <section className="py-32 lg:py-48 bg-background border-y border-black/[0.03] dark:border-white/[0.03] overflow-hidden relative">
      <div className="container mx-auto px-6 mb-20 text-center">
        <p className="text-[10px] font-black text-muted-foreground/40 dark:text-white/20 uppercase tracking-[0.5em]">
          Empowering Leading Global Fleets
        </p>
      </div>
      
      <div className="relative flex overflow-x-hidden">
        <div className="flex animate-marquee whitespace-nowrap gap-12 items-center py-4">
          {logos.map((brand, i) => (
            <div key={i} className="flex items-center gap-2 group grayscale hover:grayscale-0 transition-all duration-300">
              <div className="w-10 h-10 rounded-lg bg-muted flex items-center justify-center font-bold text-muted-foreground group-hover:text-foreground">
                {brand.name[0]}
              </div>
              <span className="text-xl font-bold text-muted-foreground group-hover:text-foreground tracking-tight">
                {brand.name}
              </span>
            </div>
          ))}
        </div>
        
        {/* Gradient overlays for smooth fading edges */}
        <div className="absolute inset-y-0 left-0 w-32 bg-gradient-to-r from-background to-transparent z-10"></div>
        <div className="absolute inset-y-0 right-0 w-32 bg-gradient-to-l from-background to-transparent z-10"></div>
      </div>
    </section>
  );
}
