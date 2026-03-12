"use client";

import { useState, useEffect } from "react";
import { dashboardConfig } from "@/config/dashboard";
import type { AgentStatus } from "@/config/dashboard";

const getStatusColor = (status: AgentStatus) => {
  switch (status) {
    case "Active": return "bg-brand-teal text-brand-teal ring-brand-teal/20";
    case "Idle": return "bg-muted-foreground text-muted-foreground ring-muted-foreground/20";
    case "Warning": return "bg-amber-500 text-amber-600 ring-amber-500/20";
    case "Error": return "bg-red-500 text-red-600 ring-red-500/20";
    default: return "bg-muted text-muted-foreground ring-muted/20";
  }
};

const getStatusStyle = (status: AgentStatus) => {
  if (status === "Warning") return "border-amber-200 bg-amber-50/10 dark:bg-amber-900/10";
  if (status === "Error") return "border-red-200 bg-red-50/10 dark:bg-red-900/10";
  return "bg-card border-border";
};

export function AgentPulse() {
  const { agents } = dashboardConfig;

  // Animate load percentages for Active agents with subtle ±4% fluctuation
  const [loads, setLoads] = useState<Record<string, number>>(
    Object.fromEntries(agents.map((a) => [a.id, a.loadPercentage]))
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setLoads((prev) => {
        const next = { ...prev };
        agents.forEach((agent) => {
          if (agent.status === "Active") {
            const delta = (Math.random() - 0.5) * 8; // ±4%
            next[agent.id] = Math.max(5, Math.min(99, agent.loadPercentage + delta));
          }
        });
        return next;
      });
    }, 3000);
    return () => clearInterval(interval);
  }, [agents]);

  const onlineCount = agents.filter((a) => a.status !== "Idle").length;

  return (
    <section data-purpose="agent-pulse">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-brand-blue animate-pulse shadow-[0_0_8px_rgba(37,117,252,0.8)]"></span>
          Agent Pulse
        </h3>
        <span className="text-xs text-muted-foreground font-medium">{onlineCount} Agents Online</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.id}
            title={agent.lastAction ? `${agent.lastAction.message} — ${agent.lastAction.timestamp}` : agent.name}
            className={`p-3 rounded-xl border flex flex-col gap-2 transition-all hover:shadow-md cursor-default ${getStatusStyle(agent.status)}`}
          >
            <div className="flex items-center justify-between">
              <span className={`text-[10px] font-bold ${agent.status === "Warning" ? "text-amber-600 dark:text-amber-500" : "text-muted-foreground"}`}>
                {agent.id}
              </span>
              <span className={`w-2 h-2 rounded-full ${getStatusColor(agent.status).split(" ")[0]}`}></span>
            </div>
            <div className="text-xs font-semibold text-foreground truncate">{agent.name}</div>

            <div className="w-full bg-muted h-1.5 rounded-full overflow-hidden mt-1">
              <div
                className={`h-full rounded-full transition-all duration-1000 ${getStatusColor(agent.status).split(" ")[0]}`}
                style={{ width: `${Math.round(loads[agent.id] ?? agent.loadPercentage)}%` }}
              ></div>
            </div>
            <span className="text-[9px] text-muted-foreground font-mono text-right">
              {Math.round(loads[agent.id] ?? agent.loadPercentage)}%
            </span>
          </div>
        ))}
      </div>
    </section>
  );
}
