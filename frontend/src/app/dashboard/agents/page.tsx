"use client";

import { dashboardConfig } from "@/config/dashboard";
import { 
  Bot, Activity, BrainCircuit, ShieldCheck, 
  Scale, MessageSquare, GraduationCap, 
  DatabaseZap, ShieldAlert, GitMerge, HeartPulse
} from "lucide-react";

export default function AgentsPage() {
  const { agents } = dashboardConfig;

  const getAgentIcon = (name: string) => {
    switch (name) {
      case "Safety": return <ShieldCheck className="w-6 h-6" />;
      case "Ingestion Quality": return <DatabaseZap className="w-6 h-6" />;
      case "PII Scrubber": return <ShieldAlert className="w-6 h-6" />;
      case "Orchestrator": return <GitMerge className="w-6 h-6" />;
      case "Context": return <BrainCircuit className="w-6 h-6" />;
      case "Behavior": return <Activity className="w-6 h-6" />;
      case "Sentiment": return <HeartPulse className="w-6 h-6" />;
      case "Advocacy": return <MessageSquare className="w-6 h-6" />;
      case "Coaching": return <GraduationCap className="w-6 h-6" />;
      default: return <Bot className="w-6 h-6" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "Governance": return "bg-slate-500/10 text-slate-500 border-slate-500/20";
      case "Orchestration": return "bg-brand-blue/10 text-brand-blue border-brand-blue/20";
      case "Analysis": return "bg-purple-500/10 text-purple-500 border-purple-500/20";
      case "Action": return "bg-brand-teal/10 text-brand-teal border-brand-teal/20";
      default: return "bg-muted text-muted-foreground";
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="agents-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Multi-Agent Intelligence</h2>
          <p className="text-muted-foreground text-sm">Orchestrating 9 specialized autonomous agents for fleet governance.</p>
        </div>
        <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm">
          System Audit Logs
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {agents.map((agent) => (
          <div key={agent.id} className="bg-card rounded-xl border border-border p-6 shadow-sm flex flex-col gap-4 relative overflow-hidden group hover:border-brand-blue/30 transition-colors">
            {/* Background motif */}
            <div className="absolute -right-6 -top-6 text-muted-foreground/5 transform rotate-12 group-hover:text-brand-blue/5 transition-colors">
              {getAgentIcon(agent.name)}
            </div>
            
            <div className="flex items-start justify-between relative z-10">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  agent.status === 'Active' ? 'bg-brand-teal/10 text-brand-teal' :
                  agent.status === 'Warning' ? 'bg-amber-500/10 text-amber-500' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {getAgentIcon(agent.name)}
                </div>
                <div>
                  <h3 className="font-bold text-foreground leading-tight">{agent.name}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border ${getTypeColor(agent.type)}`}>
                      {agent.type}
                    </span>
                    <p className="text-[10px] text-muted-foreground font-mono">{agent.id}</p>
                  </div>
                </div>
              </div>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full ${
                agent.status === 'Active' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
                agent.status === 'Warning' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                'bg-muted-foreground/10 text-muted-foreground border border-border'
              }`}>
                {agent.status}
              </span>
            </div>

            <div className="relative z-10">
              <p className="text-xs text-muted-foreground line-clamp-2 h-8">
                {agent.description}
              </p>
            </div>

            <div className="space-y-2 relative z-10">
              <div className="flex justify-between text-[10px]">
                <span className="text-muted-foreground font-bold uppercase tracking-wider">Activity Load</span>
                <span className="font-mono font-bold text-foreground">{agent.loadPercentage}%</span>
              </div>
              <div className="w-full bg-muted h-1.5 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ${
                    agent.status === 'Warning' ? 'bg-amber-500' : 
                    agent.status === 'Idle' ? 'bg-muted-foreground/30' : 
                    'bg-brand-teal'
                  }`}
                  style={{ width: `${agent.loadPercentage}%` }}
                ></div>
              </div>
            </div>

            <div className="mt-auto pt-4 border-t border-border flex justify-between items-center relative z-10">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Uptime: 99.9%</span>
              <button className="text-xs text-brand-blue font-semibold hover:underline">View Logs</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
