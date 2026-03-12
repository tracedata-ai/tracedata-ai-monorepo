export default function Home() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Welcome to TraceData</h2>
        <p className="text-muted-foreground">Your AI-powered fleet management and telemetry platform.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-8 glass-card rounded-2xl border border-border/50 relative overflow-hidden group hover:shadow-premium transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <div className="w-24 h-24 rounded-full bg-brand-blue blur-3xl" />
          </div>
          <h3 className="text-xl font-bold mb-2">Fleet Overview</h3>
          <p className="text-muted-foreground mb-4">Monitor your active routes and vehicle status in real-time.</p>
          <div className="text-3xl font-bold text-brand-blue">Active</div>
        </div>

        <div className="p-8 glass-card rounded-2xl border border-border/50 relative overflow-hidden group hover:shadow-premium transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <div className="w-24 h-24 rounded-full bg-brand-teal blur-3xl" />
          </div>
          <h3 className="text-xl font-bold mb-2">Trip Analytics</h3>
          <p className="text-muted-foreground mb-4">Deep dive into driver performance and trip history.</p>
          <div className="text-3xl font-bold text-brand-teal">89% Efficiency</div>
        </div>

        <div className="p-8 glass-card rounded-2xl border border-border/50 relative overflow-hidden group hover:shadow-premium transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <div className="w-24 h-24 rounded-full bg-red-500 blur-3xl" />
          </div>
          <h3 className="text-xl font-bold mb-2">Issue Alerts</h3>
          <p className="text-muted-foreground mb-4">Stay on top of vehicle health and safety incidents.</p>
          <div className="text-3xl font-bold text-red-500">2 Critical</div>
        </div>
      </div>
    </div>
  );
}
