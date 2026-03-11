import { landingConfig } from "@/config/landing";

export function DashboardPreview() {
  const { dashboardPreview } = landingConfig;
  
  return (
    <section className="py-24 overflow-hidden bg-muted/20" data-purpose="dashboard-preview">
      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="lg:w-1/3">
            <h2 className="text-sm font-bold text-brand-blue uppercase tracking-[0.3em] mb-4">
              {dashboardPreview.subheading}
            </h2>
            <h3 className="text-4xl font-bold mb-6 fragmented-header text-foreground">
              {dashboardPreview.title}
            </h3>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              {dashboardPreview.description}
            </p>
            <ul className="space-y-4">
              {dashboardPreview.features.map((feature, i) => (
                <li key={i} className="flex items-center gap-3 text-sm text-foreground">
                  <span className={`w-2 h-2 rounded-full bg-${feature.color}`}></span>
                  {feature.text}
                </li>
              ))}
            </ul>
          </div>
          
          <div className="lg:w-2/3 relative">
            <div className="bg-card border border-border p-2 rounded-3xl overflow-hidden shadow-2xl relative transition-colors">
              <div className="h-8 bg-muted/50 rounded-t-xl flex items-center px-4 gap-2 mb-2">
                <div className="w-2 h-2 rounded-full bg-red-400"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-400"></div>
                <div className="w-2 h-2 rounded-full bg-green-400"></div>
              </div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                alt={dashboardPreview.visualAlt}
                className="w-full rounded-b-xl border border-border dark:opacity-90"
                src={dashboardPreview.visualSrc}
              />
            </div>
            
            <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-[image:var(--background-image-gradient-brand)] motif-fragment opacity-20 blur-lg -z-10"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
