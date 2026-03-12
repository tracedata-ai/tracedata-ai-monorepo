"use client";

import { useState } from "react";
import { FileText, Download, Calendar, ChevronDown, ChevronUp, Bot, BarChart3 } from "lucide-react";

interface Report {
  id: string;
  name: string;
  date: string;
  size: string;
  type: "PDF" | "CSV" | "JSON";
  agentTag: string;
  confidenceScore: number;
  aiSummary: string;
}

const mockReports: Report[] = [
  {
    id: "REP-992",
    name: "Weekly Fleet Efficiency Summary",
    date: "Oct 24, 2026",
    size: "2.4 MB",
    type: "PDF",
    agentTag: "Behavior Agent",
    confidenceScore: 0.94,
    aiSummary:
      "The Behavior Agent identified a 7% improvement in fleet-wide eco-driving scores this week, driven primarily by route RT-001-A optimisations. Driver TR-9922 (Nurul Huda) achieved a perfect 98/100 trip score. Chen Wei Ming (TR-3310) was flagged for an aggressive acceleration pattern in CBD zones — Coaching Agent has scheduled a personalised feedback session with XAI-backed feature importance highlighting Rapid Acceleration as the primary negative contributor (−0.20 SHAP value).",
  },
  {
    id: "REP-991",
    name: "Driver Burnout Heatmap Export",
    date: "Oct 23, 2026",
    size: "1.1 MB",
    type: "CSV",
    agentTag: "Sentiment Agent",
    confidenceScore: 0.87,
    aiSummary:
      "The Sentiment Agent detected a 12% decline in driver morale on East Coast routes (RT-003-A/B) this week, correlated with extended shift durations averaging 9.4 hours. High burnout risk is flagged for TR-0114 (Muthu Kumar) during night shifts — micro-steering corrections spiked between 23:00–01:00. Coaching Agent has scheduled 3 wellbeing check-ins. Advocacy Agent logged 1 related appeal (app-3: Inactivity Flag Dispute).",
  },
  {
    id: "REP-990",
    name: "Agent Decision Trace Log (AG-04)",
    date: "Oct 22, 2026",
    size: "15.8 MB",
    type: "JSON",
    agentTag: "Orchestrator",
    confidenceScore: 0.99,
    aiSummary:
      "Full decision trace for the Behavior Agent (AG-04) across 142 trip evaluations this cycle. Orchestrator dispatched 6 escalations to the Safety Agent following harsh-event clusters detected on RT-004-B. Issue IDX-772 (EV Battery Thermal Spike on VEH-4501) was autonomously flagged and the charge cycle was halted within 60 seconds — zero driver intervention required. Average agent response latency across all dispatches: 340ms. Fairness audit confirmed no statistically significant scoring bias across driver demographic segments (max SPD: 0.18).",
  },
];

const typeColor: Record<string, string> = {
  PDF: "text-red-400 bg-red-500/10 border-red-500/20",
  CSV: "text-green-400 bg-green-500/10 border-green-500/20",
  JSON: "text-amber-400 bg-amber-500/10 border-amber-500/20",
};

export default function ReportsPage() {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const toggle = (id: string) => setExpandedId((prev) => (prev === id ? null : id));

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="reports-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Analytics & Reports</h2>
          <p className="text-muted-foreground text-sm">AI-generated insights from the agent orchestration pipeline.</p>
        </div>
        <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Generate New Report
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold flex items-center gap-2">
            <BarChart3 className="w-4 h-4" /> Total Reports Generated
          </span>
          <span className="text-3xl font-bold text-foreground">142</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold">Storage Used</span>
          <span className="text-3xl font-bold text-foreground">8.4 GB</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold">Scheduled Reports</span>
          <span className="text-3xl font-bold text-foreground">3 <span className="text-sm font-medium text-muted-foreground">/ week</span></span>
        </div>
      </div>

      {/* Report cards */}
      <div>
        <h3 className="text-lg font-bold text-foreground mb-4">Recent Reports</h3>
        <div className="space-y-3">
          {mockReports.map((report) => {
            const isExpanded = expandedId === report.id;
            return (
              <div
                key={report.id}
                className={`bg-card rounded-xl border transition-all shadow-sm overflow-hidden ${isExpanded ? "border-brand-blue/30" : "border-border"}`}
              >
                {/* Row */}
                <div
                  className="p-4 flex items-center justify-between gap-4 cursor-pointer hover:bg-muted/20 transition-colors"
                  onClick={() => toggle(report.id)}
                >
                  <div className="flex items-center gap-4 flex-1 min-w-0">
                    <div className={`p-2.5 rounded-lg flex-shrink-0 ${isExpanded ? "bg-brand-blue/10 text-brand-blue" : "bg-muted text-muted-foreground"}`}>
                      <FileText className="w-5 h-5" />
                    </div>
                    <div className="min-w-0">
                      <h4 className={`font-bold text-sm transition-colors ${isExpanded ? "text-brand-blue" : "text-foreground"}`}>
                        {report.name}
                      </h4>
                      <div className="flex items-center flex-wrap gap-2 mt-1 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {report.date}</span>
                        <span>•</span>
                        <span className="font-mono">{report.size}</span>
                        <span>•</span>
                        <span className={`text-[9px] font-bold uppercase px-1.5 py-0.5 rounded border ${typeColor[report.type]}`}>{report.type}</span>
                        <span className="flex items-center gap-1 text-[10px] bg-muted px-2 py-0.5 rounded-full border border-border">
                          <Bot className="w-3 h-3" /> {report.agentTag}
                        </span>
                        <span className="text-[10px] font-mono text-brand-teal font-bold">
                          {Math.round(report.confidenceScore * 100)}% confidence
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button
                      onClick={(e) => e.stopPropagation()}
                      className="p-2 text-muted-foreground hover:text-brand-blue hover:bg-brand-blue/10 rounded-lg transition-colors"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    {isExpanded ? (
                      <ChevronUp className="w-4 h-4 text-brand-blue" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                </div>

                {/* Expanded AI summary */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-border/50">
                    <div className="mt-4 flex items-start gap-3">
                      <div className="p-1.5 bg-brand-blue/10 rounded-lg flex-shrink-0 mt-0.5">
                        <Bot className="w-4 h-4 text-brand-blue" />
                      </div>
                      <div>
                        <p className="text-[10px] font-bold uppercase tracking-wider text-brand-blue mb-2">AI Summary — {report.agentTag}</p>
                        <p className="text-sm text-muted-foreground leading-relaxed">{report.aiSummary}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
