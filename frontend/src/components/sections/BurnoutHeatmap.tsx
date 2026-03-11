export function BurnoutHeatmap() {
  return (
    <section className="py-24 bg-muted/30 border-t border-border">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
          Predictive Wellness
        </h2>
        <h3 className="text-4xl md:text-5xl font-bold mb-12 fragmented-header text-foreground">
          Operational Burnout Heatmap
        </h3>
        
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="col-span-2 bg-card p-6 rounded-3xl border border-border shadow-md transition-colors">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              alt="Burnout Heatmap"
              className="w-full rounded-xl border border-border dark:opacity-90"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuDgHewQRcjfFoOJRPcpOU2flMlbQ7ot34CCyMOZBWf_Sp4nzYKKxKROvqs-QwyfyrmLFk_naWyAw_whvaFDRiJOgXG0QvrbWu2W8R9TV3cw2LQ-GroMcszXK6GQeM2VU2MFeQ9cDOyQxZ9YMgqZ0TYlRnnq6mpVmhDdpsi1MZ5GbUl1KvmTU_g15R7TTm8bYmbujcvPljlHXjYpt9GG_FClqwWz5pUuznUA4EWuuwMIKWcfpOr6ka0GnbF6_9J-_E-gbCzILNIFsYrR"
            />
          </div>
          
          <div className="flex flex-col justify-center gap-6 text-left">
            <div className="p-6 bg-card border border-border rounded-2xl shadow-sm transition-colors">
              <h5 className="text-brand-teal font-bold uppercase text-xs mb-2">
                Wellness Interventions
              </h5>
              <p className="text-muted-foreground text-sm">
                AI-triggered rest periods and task reallocation based on cognitive load metrics.
              </p>
            </div>
            
            <div className="p-6 bg-card border border-border rounded-2xl shadow-sm transition-colors">
              <h5 className="text-brand-blue font-bold uppercase text-xs mb-2">
                Retention Modeling
              </h5>
              <p className="text-muted-foreground text-sm">
                Predicting turnover risk 30 days in advance using behavior agent sentiment analysis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
