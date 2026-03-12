export default function RoutesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Routes</h2>
        <p className="text-muted-foreground">Manage and monitor vehicle delivery routes.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Total Routes</h3>
          <p className="text-3xl font-bold text-brand-blue">12</p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Active Routes</h3>
          <p className="text-3xl font-bold text-brand-teal">8</p>
        </div>
      </div>

      <div className="w-full glass-card rounded-xl border border-border/50 min-h-[400px] flex items-center justify-center">
        <p className="text-muted-foreground italic">Route list coming soon...</p>
      </div>
    </div>
  );
}
