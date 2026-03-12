"use client";

import { useState } from "react";
import { dashboardConfig } from "@/config/dashboard";
import { AgentFlowDiagram } from "@/components/shared/AgentFlowDiagram";
import {
  Bot, Activity, BrainCircuit, ShieldCheck,
  MessageSquare, GraduationCap,
  DatabaseZap, ShieldAlert, GitMerge, HeartPulse,
  Network, Clock, Zap, ChevronRight,
} from "lucide-react";
import type { Agent } from "@/lib/api/schemas/agent.schema";

// ─── Helpers ────────────────────────────────────────────────────────────────

const getAgentIcon = (name: string) => {
  switch (name) {
    case "Safety": return <ShieldCheck className="w-5 h-5" />;
    case "Ingestion Quality": return <DatabaseZap className="w-5 h-5" />;
    case "PII Scrubber": return <ShieldAlert className="w-5 h-5" />;
    case "Orchestrator": return <GitMerge className="w-5 h-5" />;
    case "Context": return <BrainCircuit className="w-5 h-5" />;
    case "Behavior": return <Activity className="w-5 h-5" />;
    case "Sentiment": return <HeartPulse className="w-5 h-5" />;
    case "Advocacy": return <MessageSquare className="w-5 h-5" />;
    case "Coaching": return <GraduationCap className="w-5 h-5" />;
    default: return <Bot className="w-5 h-5" />;
  }
};

const getTypeColor = (type: string) => {
  switch (type) {
    case "Governance": return "bg-slate-500/10 text-slate-400 border-slate-500/20";
    case "Orchestration": return "bg-brand-blue/10 text-brand-blue border-brand-blue/20";
    case "Analysis": return "bg-purple-500/10 text-purple-400 border-purple-500/20";
    case "Action": return "bg-brand-teal/10 text-brand-teal border-brand-teal/20";
    default: return "bg-muted text-muted-foreground";
  }
};

const getStatusBadge = (status: Agent["status"]) => {
  switch (status) {
    case "Active": return "bg-brand-teal/10 text-brand-teal border-brand-teal/20";
    case "Warning": return "bg-amber-500/10 text-amber-500 border-amber-500/20";
    case "Idle": return "bg-muted-foreground/10 text-muted-foreground border-border";
    case "Error": return "bg-red-500/10 text-red-500 border-red-500/20";
    default: return "bg-muted text-muted-foreground";
  }
};

// ─── Architecture Tab ────────────────────────────────────────────────────────

function ArchitectureView({ agents, highlightedId, onHighlight }: {
  agents: Agent[];
  highlightedId: string | null;
  onHighlight: (id: string | null) => void;
}) {
  const highlightedAgent = agents.find((a) => a.id === highlightedId);

  return (
    <div className="space-y-6">
      {/* Tier flow diagram */}
      <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
        <div className="flex items-center gap-2 mb-6">
          <Network className="w-4 h-4 text-brand-blue" />
          <h3 className="text-sm font-bold text-foreground">Agent Tier Architecture</h3>
          <span className="text-[10px] text-muted-foreground ml-auto">Click a node to highlight its card below</span>
        </div>
        <AgentFlowDiagram
          interactive
          onNodeClick={(id) => onHighlight(highlightedId === id ? null : id)}
          highlightedId={highlightedId ?? undefined}
        />
      </div>

      {/* Highlighted agent detail (if selected) */}
      {highlightedAgent && (
        <div className="bg-brand-blue/5 border border-brand-blue/20 rounded-xl p-5 flex gap-4 items-start">
          <div className={`p-2 rounded-lg ${getTypeColor(highlightedAgent.type)}`}>
            {getAgentIcon(highlightedAgent.name)}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-bold text-foreground">{highlightedAgent.name}</h4>
              <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border ${getTypeColor(highlightedAgent.type)}`}>{highlightedAgent.type}</span>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${getStatusBadge(highlightedAgent.status)}`}>{highlightedAgent.status}</span>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{highlightedAgent.description}</p>
            {highlightedAgent.lastAction && (
              <div className="mt-2 flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="w-3 h-3" />
                <span className="font-medium">{highlightedAgent.lastAction.timestamp}</span>
                <ChevronRight className="w-3 h-3" />
                <span>{highlightedAgent.lastAction.message}</span>
              </div>
            )}
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-2xl font-bold text-foreground font-mono">
              {Math.round((highlightedAgent.confidenceScore ?? 0) * 100)}%
            </div>
            <div className="text-[10px] text-muted-foreground uppercase">Confidence</div>
            {highlightedAgent.latencyMs !== undefined && (
              <div className="text-[10px] text-muted-foreground mt-1">{highlightedAgent.latencyMs}ms latency</div>
            )}
          </div>
        </div>
      )}

      {/* Agent cards grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        {agents.map((agent) => (
          <div
            key={agent.id}
            onClick={() => onHighlight(highlightedId === agent.id ? null : agent.id)}
            className={`bg-card rounded-xl border p-5 shadow-sm flex flex-col gap-3 relative overflow-hidden group cursor-pointer transition-all
              ${highlightedId === agent.id ? "border-brand-blue/40 ring-1 ring-brand-blue/20 shadow-md" : "border-border hover:border-brand-blue/30"}
            `}
          >
            <div className="absolute -right-4 -top-4 opacity-5 group-hover:opacity-10 transition-opacity">
              {getAgentIcon(agent.name)}
            </div>

            <div className="flex items-start justify-between">
              <div className="flex items-center gap-2">
                <div className={`p-1.5 rounded-lg ${getTypeColor(agent.type)}`}>
                  {getAgentIcon(agent.name)}
                </div>
                <div>
                  <h3 className="font-bold text-foreground text-sm leading-tight">{agent.name}</h3>
                  <p className="text-[9px] font-mono text-muted-foreground">{agent.id}</p>
                </div>
              </div>
              <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${getStatusBadge(agent.status)}`}>
                {agent.status}
              </span>
            </div>

            <p className="text-[11px] text-muted-foreground line-clamp-2">{agent.description}</p>

            {/* Load bar */}
            <div className="space-y-1">
              <div className="flex justify-between text-[9px] text-muted-foreground font-bold uppercase tracking-wider">
                <span>Load</span>
                <span className="font-mono text-foreground">{agent.loadPercentage}%</span>
              </div>
              <div className="w-full bg-muted h-1 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full ${agent.status === "Warning" ? "bg-amber-500" : agent.status === "Idle" ? "bg-muted-foreground/30" : "bg-brand-teal"}`}
                  style={{ width: `${agent.loadPercentage}%` }}
                />
              </div>
            </div>

            {/* Last action */}
            {agent.lastAction && (
              <div className="text-[10px] text-muted-foreground border-t border-border pt-2 flex items-start gap-1">
                <Zap className="w-3 h-3 flex-shrink-0 mt-0.5 text-brand-blue" />
                <span className="line-clamp-2">{agent.lastAction.message}</span>
              </div>
            )}

            {/* Confidence + latency */}
            <div className="flex justify-between items-center border-t border-border pt-2">
              <span className="text-[9px] text-muted-foreground uppercase font-bold">
                Confidence: {agent.confidenceScore !== undefined ? `${Math.round(agent.confidenceScore * 100)}%` : "—"}
              </span>
              <span className="text-[9px] text-muted-foreground font-mono">
                {agent.latencyMs !== undefined ? `${agent.latencyMs}ms` : "—"}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function AgentsPage() {
  const { agents } = dashboardConfig;
  const [highlightedId, setHighlightedId] = useState<string | null>(null);

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="agents-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Multi-Agent Intelligence</h2>
          <p className="text-muted-foreground text-sm">Orchestrating {agents.length} specialized autonomous agents for fleet governance.</p>
        </div>
        <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm">
          System Audit Logs
        </button>
      </div>

      <ArchitectureView
        agents={agents}
        highlightedId={highlightedId}
        onHighlight={setHighlightedId}
      />
    </div>
  );
}
