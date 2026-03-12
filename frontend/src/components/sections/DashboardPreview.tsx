import { landingConfig } from "@/config/landing";
import { CheckCircle2 } from "lucide-react";
import { SectionHeader } from "../landing/SectionHeader";
import { SectionWrapper } from "../landing/SectionWrapper";
import { BrowserMockup } from "../landing/BrowserMockup";

export function DashboardPreview() {
  const { transparency } = landingConfig;
  
  return (
    <SectionWrapper id="transparency" variant="surface">
      <div className="flex flex-col lg:flex-row items-center gap-32">
        <div className="lg:w-1/2">
          <SectionHeader 
            badge={transparency.subheading}
            title={transparency.title}
            description={transparency.description}
            align="left"
            className="mb-12"
          />
          
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
        
        <div className="lg:w-1/2 relative">
          <BrowserMockup 
            src={transparency.visualSrc} 
            alt={transparency.visualAlt} 
          />
          
          {/* Massive Ambient Lighting */}
          <div className="absolute -bottom-20 -right-20 w-[30rem] h-[30rem] bg-brand-teal/5 dark:bg-brand-teal/10 blur-[150px] -z-10 rounded-full"></div>
          <div className="absolute -top-20 -left-20 w-[30rem] h-[30rem] bg-brand-blue/5 dark:bg-brand-blue/10 blur-[150px] -z-10 rounded-full"></div>
        </div>
      </div>
    </SectionWrapper>
  );
}
