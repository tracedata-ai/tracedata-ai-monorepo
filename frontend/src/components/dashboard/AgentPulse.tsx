import { dashboardConfig, AgentPulseData } from "@/config/dashboard";

const getStatusColor = (status: AgentPulseData["status"]) => {
  switch (status) {
    case "Active": return "bg-brand-teal text-brand-teal ring-brand-teal/20";
    case "Idle": return "bg-muted-foreground text-muted-foreground ring-muted-foreground/20";
    case "Warning": return "bg-amber-500 text-amber-600 ring-amber-500/20";
    case "Error": return "bg-red-500 text-red-600 ring-red-500/20";
    default: return "bg-muted text-muted-foreground ring-muted/20";
  }
};

const getStatusStyle = (status: AgentPulseData["status"]) => {
  if (status === "Warning") {
    return "border-amber-200 bg-amber-50/10 dark:bg-amber-900/10";
  }
  if (status === "Error") {
    return "border-red-200 bg-red-50/10 dark:bg-red-900/10";
  }
  return "bg-card border-border";
};

export function AgentPulse() {
  const { agents } = dashboardConfig;

  return (
    <section data-purpose="agent-pulse">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-brand-blue animate-pulse shadow-[0_0_8px_rgba(37,117,252,0.8)]"></span>
          Agent Pulse
        </h3>
        <span className="text-xs text-muted-foreground font-medium">8 Agents Online</span>
      </div>
      
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        {agents.map((agent) => (
          <div 
            key={agent.id} 
            className={`p-3 rounded-xl border flex flex-col gap-2 transition-all hover:shadow-md ${getStatusStyle(agent.status)}`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-[10px] font-bold ${agent.status === 'Warning' ? 'text-amber-600 dark:text-amber-500' : 'text-muted-foreground'}`}>
                {agent.id}
              </span>
              <span className={`w-2 h-2 rounded-full ${getStatusColor(agent.status).split(' ')[0]}`}></span>
            </div>
            <div className="text-xs font-semibold text-foreground">{agent.status}</div>
            
            <div className="w-full bg-muted h-1.5 rounded-full overflow-hidden mt-1">
              <div 
                className={`h-full rounded-full transition-all duration-1000 ${getStatusColor(agent.status).split(' ')[0]}`}
                style={{ width: `${agent.loadPercentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
