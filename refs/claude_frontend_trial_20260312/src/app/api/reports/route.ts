import { NextResponse } from "next/server";
import { ReportSchema } from "@/lib/api/schemas";
import type { ListReportsResponse } from "@/lib/api/contracts";
import { z } from "zod";

const mockReports = [
  {
    id: "REP-992",
    name: "Weekly Fleet Efficiency Summary",
    date: "2026-10-24",
    size: "2.4 MB",
    type: "PDF" as const,
    agentTag: "Behavior Agent",
    confidenceScore: 0.94,
    aiSummary:
      "The Behavior Agent identified a 7% improvement in fleet-wide eco-driving scores this week, driven primarily by route RT-001-A optimisations. Driver TR-9922 (Nurul Huda) achieved a perfect 98/100 trip score. Chen Wei Ming (TR-3310) flagged for aggressive acceleration in CBD zones — Coaching Agent has scheduled a personalised feedback session.",
  },
  {
    id: "REP-991",
    name: "Driver Burnout Heatmap Export",
    date: "2026-10-23",
    size: "1.1 MB",
    type: "CSV" as const,
    agentTag: "Sentiment Agent",
    confidenceScore: 0.87,
    aiSummary:
      "The Sentiment Agent detected a 12% decline in driver morale on East Coast routes (RT-003-A/B) this week, correlated with extended shift durations averaging 9.4 hours. High burnout risk flagged for TR-0114 (Muthu Kumar) during night shifts. Coaching Agent has scheduled 3 check-ins. Advocacy Agent logged 1 related appeal (app-3).",
  },
  {
    id: "REP-990",
    name: "Agent Decision Trace Log (AG-04)",
    date: "2026-10-22",
    size: "15.8 MB",
    type: "JSON" as const,
    agentTag: "Orchestrator",
    confidenceScore: 0.99,
    aiSummary:
      "Full decision trace for the Behavior Agent (AG-04) across 142 trip evaluations. Orchestrator dispatched 6 escalations to Safety Agent following harsh-event clusters on RT-004-B. Issue IDX-772 (EV Battery Thermal Spike) was autonomously flagged and charge cycle halted within 60 seconds. Average agent response latency: 340ms.",
  },
];

export async function GET(): Promise<NextResponse<ListReportsResponse>> {
  const validated = z.array(ReportSchema).parse(mockReports);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
