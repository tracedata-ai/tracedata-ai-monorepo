import { dashboardConfig, OrchestrationEvent } from "@/config/dashboard";

const getSeverityColor = (severity: OrchestrationEvent["severity"]) => {
  switch (severity) {
    case "info": return "bg-brand-blue";
    case "warning": return "bg-amber-500";
    case "error": return "bg-red-500";
    default: return "bg-muted";
  }
};

export function LiveOrchestration() {
  const { orchestrationFeed } = dashboardConfig;

  return (
    <div className="bg-card rounded-xl border border-border flex flex-col h-[320px] shadow-sm" data-purpose="live-orchestration">
      <div className="p-4 border-b border-border flex items-center justify-between sticky top-0 bg-card rounded-t-xl z-10">
        <h3 className="text-sm font-bold text-foreground">Live Orchestration</h3>
        <div className="flex gap-1 animate-pulse">
          <span className="w-1 h-1 bg-brand-teal rounded-full shadow-[0_0_8px_rgba(13,148,136,0.8)]"></span>
          <span className="w-1 h-1 bg-brand-teal rounded-full shadow-[0_0_8px_rgba(13,148,136,0.8)] animation-delay-200"></span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {orchestrationFeed.map((event) => (
          <div key={event.id} className="flex gap-3 items-start hover:bg-muted/30 p-2 -mx-2 rounded-lg transition-colors cursor-default">
            <div className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${getSeverityColor(event.severity)}`}></div>
            <div className="flex-1">
              <p className="text-xs text-foreground leading-relaxed">
                <span className="font-bold mr-1">{event.agentId}</span>
                {event.message}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-muted-foreground uppercase font-medium">
                  {event.timestamp}
                </span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-sm font-semibold uppercase ${
                  event.severity === 'info' ? 'bg-brand-blue/10 text-brand-blue' :
                  event.severity === 'warning' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500' :
                  'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
                }`}>
                  {event.agentName}
                </span>
              </div>
            </div>
          </div>
        ))}
        {/* Placeholder for scroll indicating more events */}
        <div className="flex gap-3 opacity-50">
          <div className="mt-1 w-2 h-2 rounded-full bg-muted flex-shrink-0"></div>
          <div className="text-[10px] text-muted-foreground uppercase font-medium">Loading previous events...</div>
        </div>
      </div>
    </div>
  );
}
