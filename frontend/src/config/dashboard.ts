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

export interface DriverProfile {
  id: string;
  name: string;
  status: "Active" | "On Break" | "Off Duty";
  shiftHours: number;
  rating: number;
}

export interface TripRecord {
  id: string;
  vehicleId: string;
  driverId: string;
  status: "In Progress" | "Completed" | "Scheduled" | "Cancelled";
  origin: string;
  destination: string;
  startTime: string; // ISO
  estimatedDurationMins: number; // Initially estimated minutes
  actualDurationMins?: number; // Actual/current minutes spent
  distanceKm: number;
  currentDistanceKm?: number; // Added for in-progress tracking
  score?: number; // 0-100, populated when completed
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
      { label: "Drivers", href: "/dashboard/drivers", icon: "Users" },
      { label: "Trips", href: "/dashboard/trips", icon: "Route" },
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
  ] as AppealContest[],

  drivers: [
    { id: "TR-8291", name: "Marcus Wright", status: "Active", shiftHours: 4.5, rating: 4.8 },
    { id: "TR-4512", name: "Elena Petrov", status: "On Break", shiftHours: 6.2, rating: 4.9 },
    { id: "TR-0114", name: "Jordan Smith", status: "Off Duty", shiftHours: 0, rating: 4.5 },
    { id: "TR-9922", name: "Sarah Connor", status: "Active", shiftHours: 2.1, rating: 5.0 },
    { id: "TR-3310", name: "John Doe", status: "Active", shiftHours: 7.8, rating: 4.7 },
  ] as DriverProfile[],

  trips: [
    { id: "TRP-10042", vehicleId: "V-991", driverId: "TR-8291", status: "In Progress", origin: "Hub-7A North", destination: "Sector 4 Depot", startTime: "2026-03-11T08:30:00Z", estimatedDurationMins: 270, actualDurationMins: 185, distanceKm: 142.5, currentDistanceKm: 84.0 },
    { id: "TRP-10043", vehicleId: "V-228", driverId: "TR-4512", status: "In Progress", origin: "Downtown Core", destination: "Airport Terminal 3", startTime: "2026-03-11T10:15:00Z", estimatedDurationMins: 90, actualDurationMins: 98, distanceKm: 34.0, currentDistanceKm: 12.5 },
    { id: "TRP-10044", vehicleId: "V-045", driverId: "TR-9922", status: "Completed", origin: "Westside Logistics", destination: "East Coast Park Hub", startTime: "2026-03-11T05:00:00Z", estimatedDurationMins: 195, actualDurationMins: 180, distanceKm: 68.2, currentDistanceKm: 68.2, score: 94 },
    { id: "TRP-10045", vehicleId: "V-712", driverId: "TR-3310", status: "Scheduled", origin: "Sector 2 Base", destination: "Jurong Island", startTime: "2026-03-11T14:00:00Z", estimatedDurationMins: 150, distanceKm: 45.8, currentDistanceKm: 0 },
  ] as TripRecord[]
};
