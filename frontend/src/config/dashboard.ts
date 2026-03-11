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
  tripsCompleted: number;
  rating: number; // 1-5 consumer rating
  avgTripScore: number; // 0-100 internal score
}

export interface RouteRecord {
  id: string; // e.g. RT-001
  name: string;
  origin: string;
  destination: string;
  historicalAvgMins: number;
  standardDistanceKm: number;
  totalTripsCompleted: number;
}

export interface VehicleProfile {
  id: string; // e.g. V-991
  plateNumber: string; // e.g. SGB-1234
  model: string;
  status: "Active" | "Maintenance" | "Out Of Service";
  operatingHours: number;
}

export interface TripRecord {
  id: string;
  vehicleId: string;
  driverId: string;
  routeId: string; // Link to RouteRecord
  status: "In Progress" | "Completed" | "Scheduled" | "Cancelled";
  startTime: string; // ISO
  historicalAvgMins: number; // Snapshot from route
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
      { label: "Routes", href: "/dashboard/routes", icon: "Map" },
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
    { id: "TR-8291", name: "Marcus Wright", status: "Active", tripsCompleted: 14, rating: 4.8, avgTripScore: 92 },
    { id: "TR-4512", name: "Elena Petrov", status: "On Break", tripsCompleted: 22, rating: 4.9, avgTripScore: 96 },
    { id: "TR-0114", name: "Jordan Smith", status: "Off Duty", tripsCompleted: 0, rating: 4.5, avgTripScore: 88 },
    { id: "TR-9922", name: "Sarah Connor", status: "Active", tripsCompleted: 8, rating: 5.0, avgTripScore: 98 },
    { id: "TR-3310", name: "John Doe", status: "Active", tripsCompleted: 26, rating: 4.7, avgTripScore: 85 },
  ] as DriverProfile[],

  routes: [
    { id: "RT-001", name: "North Hub Supply Run", origin: "Hub-7A North", destination: "Sector 4 Depot", historicalAvgMins: 270, standardDistanceKm: 142.5, totalTripsCompleted: 1042 },
    { id: "RT-002", name: "Airport Express Loop", origin: "Downtown Core", destination: "Airport Terminal 3", historicalAvgMins: 90, standardDistanceKm: 34.0, totalTripsCompleted: 8550 },
    { id: "RT-003", name: "East Coast Logistics", origin: "Westside Logistics", destination: "East Coast Park Hub", historicalAvgMins: 195, standardDistanceKm: 68.2, totalTripsCompleted: 430 },
    { id: "RT-004", name: "Jurong Island Delivery", origin: "Sector 2 Base", destination: "Jurong Island", historicalAvgMins: 150, standardDistanceKm: 45.8, totalTripsCompleted: 210 },
  ] as RouteRecord[],

  trips: [
    { id: "TRP-10042", vehicleId: "V-991", driverId: "TR-8291", routeId: "RT-001", status: "In Progress", startTime: "2026-03-11T08:30:00Z", historicalAvgMins: 270, actualDurationMins: 185, distanceKm: 142.5, currentDistanceKm: 84.0 },
    { id: "TRP-10043", vehicleId: "V-228", driverId: "TR-4512", routeId: "RT-002", status: "In Progress", startTime: "2026-03-11T10:15:00Z", historicalAvgMins: 90, actualDurationMins: 98, distanceKm: 34.0, currentDistanceKm: 12.5 },
    { id: "TRP-10044", vehicleId: "V-045", driverId: "TR-9922", routeId: "RT-003", status: "Completed", startTime: "2026-03-11T05:00:00Z", historicalAvgMins: 195, actualDurationMins: 180, distanceKm: 68.2, currentDistanceKm: 68.2, score: 94 },
    { id: "TRP-10045", vehicleId: "V-712", driverId: "TR-3310", routeId: "RT-004", status: "Scheduled", startTime: "2026-03-11T14:00:00Z", historicalAvgMins: 150, distanceKm: 45.8, currentDistanceKm: 0 },
  ] as TripRecord[],

  vehicles: [
    { id: "V-991", plateNumber: "SGB-1234M", model: "EV-Transit Pro", status: "Active", operatingHours: 1250 },
    { id: "V-228", plateNumber: "SGB-5678X", model: "EV-Transit Pro", status: "Active", operatingHours: 840 },
    { id: "V-045", plateNumber: "SGC-9012K", model: "Heavy Hauler 500", status: "Maintenance", operatingHours: 3420 },
    { id: "V-712", plateNumber: "SGB-3456P", model: "EV-Transit Pro", status: "Active", operatingHours: 150 },
  ] as VehicleProfile[]
};
