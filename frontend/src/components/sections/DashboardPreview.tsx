import { landingConfig } from "@/config/landing";
import { CheckCircle2 } from "lucide-react";

export function DashboardPreview() {
  const { transparency } = landingConfig;
  
  return (
    <section className="section-padding overflow-hidden bg-brand-surface dark:bg-[#0b1222] relative" id="transparency">
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-black/[0.03] dark:via-white/[0.03] to-transparent"></div>
      
      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row items-center gap-32">
          <div className="lg:w-1/2">
            <h2 className="text-[10px] font-black text-brand-blue uppercase tracking-[0.4em] mb-6 opacity-60">
              {transparency.subheading}
            </h2>
            <h3 className="text-5xl md:text-7xl font-black mb-10 tracking-[-0.04em] text-foreground dark:text-white text-balance leading-[0.9]">
              {transparency.title}
            </h3>
            <p className="text-2xl text-muted-foreground dark:text-white/40 mb-12 leading-relaxed font-medium tracking-tight">
              {transparency.description}
            </p>
            
            <div className="space-y-8">
              {transparency.features.map((feature, i) => (
                <div key={i} className="flex items-center gap-5 group">
                  <div className="flex-shrink-0 w-8 h-8 rounded-xl bg-brand-teal/10 dark:bg-brand-teal/5 border border-brand-teal/20 dark:border-brand-teal/10 flex items-center justify-center text-brand-teal group-hover:scale-110 transition-transform">
                    <CheckCircle2 size={18} />
                  </div>
                  <div>
                    <p className="text-xl font-black text-foreground dark:text-white uppercase tracking-tight">{feature.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="lg:w-1/2 relative group">
            <div className="glass-card p-3 rounded-[3rem] border border-black/[0.05] dark:border-white/[0.05] shadow-[0_60px_100px_-20px_rgba(0,0,0,0.2)] dark:shadow-[0_60px_100px_-20px_rgba(0,0,0,0.6)] relative z-10 transition-transform duration-700 group-hover:scale-[1.02] bg-white/50 dark:bg-white/[0.03]">
              <div className="h-12 bg-black/5 dark:bg-white/5 rounded-t-[2.2rem] flex items-center px-8 gap-3 mb-3 border-b border-black/[0.03] dark:border-white/[0.03]">
                <div className="w-3 h-3 rounded-full bg-red-400 opacity-40"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400 opacity-40"></div>
                <div className="w-3 h-3 rounded-full bg-green-400 opacity-40"></div>
                <div className="ml-6 h-5 w-40 bg-black/5 dark:bg-white/5 rounded-full"></div>
              </div>
              
              <div className="relative rounded-b-[2.2rem] overflow-hidden border-t border-black/[0.03] dark:border-white/[0.03]">
                 {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  alt={transparency.visualAlt}
                  className="w-full grayscale-[10%] group-hover:grayscale-0 transition-all duration-1000"
                  src={transparency.visualSrc}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
              </div>
            </div>
            
            {/* Massive Ambient Lighting */}
            <div className="absolute -bottom-20 -right-20 w-[30rem] h-[30rem] bg-brand-teal/5 dark:bg-brand-teal/10 blur-[150px] -z-10 rounded-full group-hover:bg-brand-teal/15 transition-colors duration-1000"></div>
            <div className="absolute -top-20 -left-20 w-[30rem] h-[30rem] bg-brand-blue/5 dark:bg-brand-blue/10 blur-[150px] -z-10 rounded-full group-hover:bg-brand-blue/15 transition-colors duration-1000"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
