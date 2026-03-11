import { landingConfig } from "@/config/landing";
import { CheckCircle2 } from "lucide-react";

export function DashboardPreview() {
  const { transparency } = landingConfig;
  
  return (
    <section className="section-padding overflow-hidden bg-muted/20 relative" id="transparency">
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-border to-transparent"></div>
      
      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row items-center gap-20">
          <div className="lg:w-1/2">
            <h2 className="text-sm font-bold text-brand-blue uppercase tracking-[0.3em] mb-4">
              {transparency.subheading}
            </h2>
            <h3 className="text-5xl font-black mb-8 tracking-tighter text-foreground text-balance">
              {transparency.title}
            </h3>
            <p className="text-xl text-muted-foreground mb-10 leading-relaxed font-medium">
              {transparency.description}
            </p>
            
            <div className="space-y-6">
              {transparency.features.map((feature, i) => (
                <div key={i} className="flex items-start gap-4">
                  <div className={`mt-1 flex-shrink-0 w-6 h-6 rounded-full bg-brand-teal/10 border border-brand-teal/20 flex items-center justify-center text-brand-teal`}>
                    <CheckCircle2 size={16} />
                  </div>
                  <div>
                    <p className="text-lg font-bold text-foreground">{feature.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="lg:w-1/2 relative">
            <div className="glass-card p-2 rounded-3xl overflow-hidden shadow-2xl relative group">
              <div className="absolute inset-0 bg-brand-blue/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <div className="h-10 bg-muted/50 rounded-t-2xl flex items-center px-6 gap-2 mb-2 border-b border-border">
                <div className="w-3 h-3 rounded-full bg-red-400 opacity-60"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400 opacity-60"></div>
                <div className="w-3 h-3 rounded-full bg-green-400 opacity-60"></div>
                <div className="ml-4 h-4 w-32 bg-muted rounded-full"></div>
              </div>
              
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                alt={transparency.visualAlt}
                className="w-full rounded-b-2xl border-t border-border dark:opacity-90"
                src={transparency.visualSrc}
              />
            </div>
            
            {/* Decorative Floating Element */}
            <div className="absolute -bottom-10 -right-10 w-64 h-64 bg-brand-teal/10 blur-[100px] -z-10 rounded-full"></div>
            <div className="absolute -top-10 -left-10 w-64 h-64 bg-brand-blue/10 blur-[100px] -z-10 rounded-full"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
