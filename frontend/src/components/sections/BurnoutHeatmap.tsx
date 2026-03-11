import { landingConfig } from "@/config/landing";

export function BurnoutHeatmap() {
  const { burnoutHeatmap } = landingConfig;
  
  return (
    <section className="py-24 bg-muted/30 border-t border-border">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
          {burnoutHeatmap.subheading}
        </h2>
        <h3 className="text-4xl md:text-5xl font-bold mb-12 fragmented-header text-foreground">
          {burnoutHeatmap.title}
        </h3>
        
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="col-span-2 bg-card p-6 rounded-3xl border border-border shadow-md transition-colors">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt={burnoutHeatmap.visualAlt}
              className="w-full rounded-xl border border-border dark:opacity-90"
              src={burnoutHeatmap.visualSrc}
            />
          </div>
          
          <div className="flex flex-col justify-center gap-6 text-left">
            {burnoutHeatmap.interventions.map((intervention, i) => (
              <div key={i} className="p-6 bg-card border border-border rounded-2xl shadow-sm transition-colors">
                <h5 className={`text-${intervention.color} font-bold uppercase text-xs mb-2`}>
                  {intervention.title}
                </h5>
                <p className="text-muted-foreground text-sm">
                  {intervention.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
