import { landingConfig } from "@/config/landing";
import { Activity } from "lucide-react";

export function EcosystemSection() {
  const { ecosystem } = landingConfig;

  return (
    <>
      <section className="py-24 bg-muted/30 relative" data-purpose="ecosystem-section">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
              {ecosystem.badge}
            </h2>
            <h3 className="text-4xl md:text-5xl font-bold fragmented-header text-foreground">
              {ecosystem.title}
            </h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {ecosystem.agents.map((agent, i) => {
              const Icon = agent.icon;
              return (
                <div key={i} className={`p-8 bg-card border border-border rounded-2xl hover:border-${agent.color}/50 hover:shadow-md transition-all cursor-pointer group`}>
                  <div className={`w-12 h-12 mb-6 bg-${agent.color}/10 rounded-lg flex items-center justify-center group-hover:bg-${agent.color}/20 transition-colors`}>
                    <Icon className={`w-6 h-6 text-${agent.color}`} />
                  </div>
                  <h4 className="font-bold text-lg mb-2 text-foreground">{agent.name}</h4>
                  <p className="text-sm text-muted-foreground">{agent.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-24 bg-background border-y border-border">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="relative">
              <div className="bg-muted p-1 rounded-3xl border border-border shadow-sm">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  alt={ecosystem.langGraph.visualAlt}
                  className="rounded-2xl w-full object-cover dark:opacity-80 transition-opacity"
                  src={ecosystem.langGraph.visualSrc}
                />
              </div>
              <div className="absolute -top-6 -left-6 px-4 py-2 bg-brand-blue rounded-full text-xs font-bold uppercase tracking-widest text-white shadow-md">
                {ecosystem.langGraph.badge}
              </div>
            </div>
            
            <div>
              <h2 className="text-sm font-bold text-brand-blue uppercase tracking-[0.3em] mb-4">
                {ecosystem.langGraph.subheading}
              </h2>
              <h3 className="text-4xl font-bold mb-6 fragmented-header text-foreground">
                {ecosystem.langGraph.title}
              </h3>
              <p className="text-muted-foreground mb-8">
                {ecosystem.langGraph.description}
              </p>
              
              <div className="space-y-6">
                {ecosystem.langGraph.features.map((feature, i) => (
                  <div key={i} className="flex items-start gap-4">
                    <Activity className={`w-6 h-6 text-${feature.color} shrink-0`} />
                    <div>
                      <h5 className="font-bold text-foreground">{feature.title}</h5>
                      <p className="text-sm text-muted-foreground">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
