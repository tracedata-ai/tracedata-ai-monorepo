import { ShieldAlert, Scale, Network, BrainCircuit, HeartHandshake, Smile, GraduationCap, Activity, ShieldCheck, AlertTriangle, AlertCircle, CheckCircle2, Clock } from "lucide-react";

// --- Types for Backend Contracts ---

export type AgentStatus = "Active" | "Idle" | "Warning" | "Error";

export interface AgentPulseData {
  id: string;
  name: string;
  status: AgentStatus;
  loadPercentage: number;
}

export interface MetricIndex {
  label: string;
  value: number; // 0-100
  trend: number; // e.g. +12
}

export interface OrchestrationEvent {
  id: string;
  agentId: string;
  agentName: string;
  message: string;
  timestamp: string; // ISO string or relative time
  severity: "info" | "warning" | "error";
}

export interface BurnoutForecastNode {
  hourOffset: number;
  sectorId: string;
  riskLevel: number; // 0-10, where 10 is highest risk
}

export interface AppealContest {
  id: string;
  driverName: string;
  driverId: string;
  driverAvatarUrl: string;
  reason: string;
  priority: "Low" | "Medium" | "Urgent";
  status: "Pending Review" | "Resolved";
}

// --- Mock Data ---

export const dashboardConfig = {
  // Navigation
  navigation: {
    title: "TraceData",
    subtitle: "Command Center",
    links: [
      { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard" },
      { label: "Agents", href: "/dashboard/agents", icon: "Bot" },
      { label: "Fleet", href: "/dashboard/fleet", icon: "Truck" },
      { label: "Issues", href: "/dashboard/issues", icon: "AlertTriangle", badge: 4 },
      { label: "Reports", href: "/dashboard/reports", icon: "BarChart3" },
      { label: "Settings", href: "/dashboard/settings", icon: "Settings" }
    ],
    user: {
      name: "Fleet Adm.",
      role: "System Root",
      avatarUrl: "https://ui-avatars.com/api/?name=Fleet+Admin&background=0d9488&color=fff"
    }
  },
  
  // Header
  header: {
    title: "Fleet Overview",
    searchPlaceholder: "Search commands or agents..."
  },

  // Widgets Data
  agents: [
    { id: "AG-01", name: "Safety", status: "Active", loadPercentage: 85 } as AgentPulseData,
    { id: "AG-02", name: "Fairness", status: "Active", loadPercentage: 92 } as AgentPulseData,
    { id: "AG-03", name: "Context", status: "Idle", loadPercentage: 0 } as AgentPulseData,
    { id: "AG-04", name: "Behavior", status: "Warning", loadPercentage: 40 } as AgentPulseData,
    { id: "AG-05", name: "Advocacy", status: "Active", loadPercentage: 78 } as AgentPulseData,
    { id: "AG-06", name: "Sentiment", status: "Idle", loadPercentage: 0 } as AgentPulseData,
    { id: "AG-07", name: "Coaching", status: "Active", loadPercentage: 65 } as AgentPulseData,
    { id: "AG-08", name: "Orchestrator", status: "Active", loadPercentage: 88 } as AgentPulseData,
  ],

  equilibrium: {
    safetyIndex: { label: "Safety Index", value: 90, trend: 2 },
    fairnessIndex: { label: "Fairness Index", value: 80, trend: -1 },
    sentimentTrend: 12,
    // Representing a 7-day sparkline style data array [0-100]
    sentimentHistory: [60, 75, 55, 80, 70, 85, 90]
  },

  orchestrationFeed: [
    { id: "evt-1", agentId: "AG-01", agentName: "Safety", message: "finalized delivery route for Hub-7A.", timestamp: "Just Now", severity: "info" },
    { id: "evt-2", agentId: "AG-05", agentName: "Advocacy", message: "re-assigned Zone 4 shifts based on weather.", timestamp: "4 mins ago", severity: "info" },
    { id: "evt-3", agentId: "AG-02", agentName: "Fairness", message: "detected route anomaly in Pacific North.", timestamp: "12 mins ago", severity: "warning" },
    { id: "evt-4", agentId: "AG-04", agentName: "Behavior", message: "flagged potential driver fatigue risk ID: 882.", timestamp: "15 mins ago", severity: "error" },
  ] as OrchestrationEvent[],

  appeals: [
    { id: "app-1", driverName: "Marcus Wright", driverId: "TR-8291", driverAvatarUrl: "https://ui-avatars.com/api/?name=Marcus+Wright&background=f87171&color=fff", reason: "Route Efficiency Penalty", priority: "Urgent", status: "Pending Review" },
    { id: "app-2", driverName: "Elena Petrov", driverId: "TR-4512", driverAvatarUrl: "https://ui-avatars.com/api/?name=Elena+Petrov&background=fcd34d&color=000", reason: "Break Schedule Alert", priority: "Medium", status: "Pending Review" },
    { id: "app-3", driverName: "Jordan Smith", driverId: "TR-0114", driverAvatarUrl: "https://ui-avatars.com/api/?name=Jordan+Smith&background=94a3b8&color=fff", reason: "Inactivity Flag Dispute", priority: "Low", status: "Pending Review" },
  ] as AppealContest[]
};
