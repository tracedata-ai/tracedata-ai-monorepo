export default function TripsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Trips</h2>
        <p className="text-muted-foreground">Real-time trip tracking and history.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Ongoing Trips</h3>
          <p className="text-3xl font-bold text-brand-blue">24</p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Completed Today</h3>
          <p className="text-3xl font-bold text-brand-teal">45</p>
        </div>
      </div>

      <div className="w-full glass-card rounded-xl border border-border/50 min-h-[400px] flex items-center justify-center">
        <p className="text-muted-foreground italic">Trip history coming soon...</p>
      </div>
    </div>
  );
}
