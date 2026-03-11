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
  status: "In Transit" | "Charging" | "Maintenance" | "Idle";
  operatingHours: number;
  driver?: string;
  location?: string;
  signal?: "Strong" | "Medium" | "Weak";
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

export interface IssueTimelineEvent {
  title: string;
  timestamp: string;
  description: string;
}

export interface IssueRecord {
  id: string; // e.g., IDX-902
  vehicleId: string; // e.g., Truck-402, or V-991 to match vehicles table
  assetName: string; // e.g., Van-105
  priority: "Critical" | "High" | "Medium" | "Low";
  type: string; // e.g., Engine, Brakes
  summary: string;
  agent: "Safety Agent" | "Context Agent" | "Behavior Agent" | "Maintenance Agent" | string;
  agentReasoning?: string;
  agentTags?: string[];
  status: "Open" | "Overdue" | "Resolved" | "Closed";
  reportedDate: string;
  resolvedDate?: string;
  technician?: string;
  resolutionAction?: string;
  timeline: IssueTimelineEvent[];
}

// --- Mock Data ---

export const dashboardConfig = {
  // Navigation
  navigation: {
    title: "TraceData",
    subtitle: "Command Center",
    links: [
      { label: "Dashboard", href: "/dashboard", icon: "LayoutDashboard", roles: ["Manager"] },
      { label: "Agents", href: "/dashboard/agents", icon: "Bot", roles: ["Manager"] },
      { label: "Drivers", href: "/dashboard/drivers", icon: "Users", roles: ["Manager"] },
      { label: "Routes", href: "/dashboard/routes", icon: "Map", roles: ["Manager", "Driver"] },
      { label: "Trips", href: "/dashboard/trips", icon: "Route", roles: ["Manager", "Driver"] },
      { label: "Fleet", href: "/dashboard/fleet", icon: "Truck", roles: ["Manager"] },
      { label: "Issues", href: "/dashboard/issues", icon: "AlertTriangle", badge: 4, roles: ["Manager", "Driver"] },
      { label: "Reports", href: "/dashboard/reports", icon: "BarChart3", roles: ["Manager"] },
      { label: "Settings", href: "/dashboard/settings", icon: "Settings", roles: ["Manager", "Driver"] }
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
    { id: "evt-1", agentId: "AG-01", agentName: "Safety", message: "finalized delivery route for Changi T1.", timestamp: "Just Now", severity: "info" },
    { id: "evt-2", agentId: "AG-05", agentName: "Advocacy", message: "re-assigned CBD shifts based on weather.", timestamp: "4 mins ago", severity: "info" },
    { id: "evt-3", agentId: "AG-02", agentName: "Fairness", message: "detected route anomaly in Jurong West.", timestamp: "12 mins ago", severity: "warning" },
    { id: "evt-4", agentId: "AG-04", agentName: "Behavior", message: "flagged potential driver fatigue risk ID: 882.", timestamp: "15 mins ago", severity: "error" },
  ] as OrchestrationEvent[],

  appeals: [
    { id: "app-1", driverName: "Lim Wei Jie", driverId: "TR-8291", driverAvatarUrl: "https://ui-avatars.com/api/?name=Lim+Wei+Jie&background=f87171&color=fff", reason: "Route Efficiency Penalty", priority: "Urgent", status: "Pending Review" },
    { id: "app-2", driverName: "Siti Aisyah", driverId: "TR-4512", driverAvatarUrl: "https://ui-avatars.com/api/?name=Siti+Aisyah&background=fcd34d&color=000", reason: "Break Schedule Alert", priority: "Medium", status: "Pending Review" },
    { id: "app-3", driverName: "Muthu Kumar", driverId: "TR-0114", driverAvatarUrl: "https://ui-avatars.com/api/?name=Muthu+Kumar&background=94a3b8&color=fff", reason: "Inactivity Flag Dispute", priority: "Low", status: "Pending Review" },
  ] as AppealContest[],

  drivers: [
    { id: "TR-8291", name: "Lim Wei Jie", status: "Active", tripsCompleted: 14, rating: 4.8, avgTripScore: 92 },
    { id: "TR-4512", name: "Siti Aisyah", status: "On Break", tripsCompleted: 22, rating: 4.9, avgTripScore: 96 },
    { id: "TR-0114", name: "Muthu Kumar", status: "Off Duty", tripsCompleted: 0, rating: 4.5, avgTripScore: 88 },
    { id: "TR-9922", name: "Nurul Huda", status: "Active", tripsCompleted: 8, rating: 5.0, avgTripScore: 98 },
    { id: "TR-3310", name: "Chen Wei Ming", status: "Active", tripsCompleted: 26, rating: 4.7, avgTripScore: 85 },
  ] as DriverProfile[],

  routes: [
    { id: "RT-001-A", name: "Changi to CBD Express", origin: "Changi Airport T3", destination: "Marina Bay Sands", historicalAvgMins: 30, standardDistanceKm: 19.5, totalTripsCompleted: 542 },
    { id: "RT-001-B", name: "CBD to Changi Express", origin: "Marina Bay Sands", destination: "Changi Airport T3", historicalAvgMins: 25, standardDistanceKm: 19.5, totalTripsCompleted: 500 },
    
    { id: "RT-002-A", name: "Sentosa Inbound", origin: "VivoCity", destination: "Sentosa Cove", historicalAvgMins: 15, standardDistanceKm: 8.0, totalTripsCompleted: 4200 },
    { id: "RT-002-B", name: "Sentosa Outbound", origin: "Sentosa Cove", destination: "VivoCity", historicalAvgMins: 18, standardDistanceKm: 8.0, totalTripsCompleted: 4350 },
    
    { id: "RT-003-A", name: "East Coast Park Outbound", origin: "Bedok Mall", destination: "East Coast Park", historicalAvgMins: 10, standardDistanceKm: 4.2, totalTripsCompleted: 215 },
    { id: "RT-003-B", name: "East Coast Park Return", origin: "East Coast Park", destination: "Bedok Mall", historicalAvgMins: 12, standardDistanceKm: 4.2, totalTripsCompleted: 215 },
    
    { id: "RT-004-A", name: "Mandai Wildlife Transfer", origin: "Boon Lay MRT", destination: "Mandai Wildlife Reserve", historicalAvgMins: 25, standardDistanceKm: 15.8, totalTripsCompleted: 110 },
    { id: "RT-004-B", name: "Mandai City Return", origin: "Mandai Wildlife Reserve", destination: "Boon Lay MRT", historicalAvgMins: 22, standardDistanceKm: 15.8, totalTripsCompleted: 100 },
  ] as RouteRecord[],

  trips: [
    { id: "TRP-10042", vehicleId: "V-991", driverId: "TR-8291", routeId: "RT-001-A", status: "In Progress", startTime: "2026-03-11T08:30:00Z", historicalAvgMins: 30, actualDurationMins: 35, distanceKm: 19.5, currentDistanceKm: 12.0 },
    { id: "TRP-10043", vehicleId: "V-228", driverId: "TR-4512", routeId: "RT-002-B", status: "In Progress", startTime: "2026-03-11T10:15:00Z", historicalAvgMins: 18, actualDurationMins: 12, distanceKm: 8.0, currentDistanceKm: 6.5 },
    { id: "TRP-10044", vehicleId: "V-045", driverId: "TR-9922", routeId: "RT-003-A", status: "Completed", startTime: "2026-03-11T05:00:00Z", historicalAvgMins: 10, actualDurationMins: 10, distanceKm: 4.2, currentDistanceKm: 4.2, score: 94 },
    { id: "TRP-10045", vehicleId: "V-712", driverId: "TR-3310", routeId: "RT-004-B", status: "Scheduled", startTime: "2026-03-11T14:00:00Z", historicalAvgMins: 22, distanceKm: 15.8, currentDistanceKm: 0 },
  ] as TripRecord[],

  vehicles: [
    { id: "VEH-8712", plateNumber: "SGB-1234M", model: "EV-Transit Pro", status: "In Transit", operatingHours: 1250, driver: "Lim Wei Jie", location: "Marina Bay Sands", signal: "Strong" },
    { id: "VEH-4501", plateNumber: "SGB-5678X", model: "EV-Transit Pro", status: "Charging", operatingHours: 840, driver: "Siti Aisyah", location: "Changi Terminal 3, EV Bay", signal: "Strong" },
    { id: "VEH-9923", plateNumber: "SGC-9012K", model: "Heavy Hauler 500", status: "Maintenance", operatingHours: 3420, driver: "Muthu Kumar", location: "Jurong West Depot", signal: "Weak" },
    { id: "VEH-1102", plateNumber: "SGB-3456P", model: "EV-Transit Pro", status: "Idle", operatingHours: 150, driver: "Nurul Huda", location: "Woodlands Checkpoint", signal: "Strong" },
    { id: "VEH-3345", plateNumber: "SGB-9876R", model: "EV-Transit Pro", status: "In Transit", operatingHours: 420, driver: "Chen Wei Ming", location: "CTE (Central Expressway)", signal: "Medium" },
  ] as VehicleProfile[],

  issues: [
    {
      id: "IDX-902",
      vehicleId: "VEH-9923",
      assetName: "Heavy Hauler 500",
      priority: "Critical",
      type: "Engine",
      summary: "Overheating",
      agent: "Safety Agent",
      status: "Resolved",
      reportedDate: "Oct 24, 2026",
      resolvedDate: "Oct 25, 2026 at 10:30 AM",
      technician: "Mike Repairs (Jurong West Depot)",
      resolutionAction: "Radiator replaced and coolant system flushed.",
      agentReasoning: "Safety Agent flagged this as critical based on sensor data showing oil temperature exceeding 220°F while at idle. Correlated with driver logs indicating 'odd noise' at stop-and-go intervals.",
      agentTags: ["Engine Thermals", "Acoustic Signal"],
      timeline: [
        { title: "Issue Detected", timestamp: "Oct 24, 2026 • 08:42 AM", description: "Automatic diagnostic scan triggered fault code P0217." },
        { title: "AI Analysis Completed", timestamp: "Oct 24, 2026 • 08:45 AM", description: "Safety Agent assigned priority 'Critical' based on route history." },
        { title: "Dispatched to Maintenance", timestamp: "Oct 24, 2026 • 09:15 AM", description: "Assigned to Jurong West Depot Service Team." }
      ]
    },
    {
      id: "IDX-844",
      vehicleId: "VEH-8712",
      assetName: "EV-Transit Pro",
      priority: "High",
      type: "Brakes",
      summary: "Wear Alert",
      agent: "Context Agent",
      status: "Open",
      reportedDate: "Oct 23, 2026",
      agentReasoning: "Context Agent correlated weather data (heavy rain expected in CBD) with deteriorating brake pad sensors (under 15% life). High risk of hydroplaning or extended stopping distance.",
      agentTags: ["Weather Context", "Sensor Telemetry"],
      timeline: [
        { title: "Sensor Threshold Reached", timestamp: "Oct 23, 2026 • 02:14 PM", description: "Brake pad wear sensor below 15%." },
        { title: "Context Agent Evaluation", timestamp: "Oct 23, 2026 • 02:18 PM", description: "Priority elevated to 'High' due to impending monsoon warning in service area." }
      ]
    },
    {
      id: "IDX-772",
      vehicleId: "VEH-4501",
      assetName: "EV-Transit Pro",
      priority: "High",
      type: "Battery",
      summary: "Thermal Spike",
      agent: "Safety Agent",
      status: "Open",
      reportedDate: "Oct 22, 2026",
      agentReasoning: "Safety Agent detected rapid temperature escalation in Cell Block 4 during fast-charging at Changi Terminal 3. Halting charge cycle to prevent thermal runaway.",
      agentTags: ["Battery Thermals", "Charge Cycle"],
      timeline: [
        { title: "Temp Anomaly Detected", timestamp: "Oct 22, 2026 • 11:30 AM", description: "Cell Block 4 temp exceeded 45°C during active charging." },
        { title: "Charge Logic Interrupted", timestamp: "Oct 22, 2026 • 11:31 AM", description: "Safety Agent terminated charge session." }
      ]
    },
    {
      id: "IDX-104",
      vehicleId: "VEH-1102",
      assetName: "EV-Transit Pro",
      priority: "Medium",
      type: "Tires",
      summary: "Low PSI",
      agent: "Maintenance Agent",
      status: "Open",
      reportedDate: "Oct 21, 2026",
      agentReasoning: "Maintenance Agent noted a slow 3 PSI drop over 48 hours on the front-left tire while operating near Woodlands Checkpoint. Likely a slow leak.",
      agentTags: ["TPMS Data", "Gradual Variance"],
      timeline: [
        { title: "Pressure Drop Flagged", timestamp: "Oct 19, 2026 • 09:00 AM", description: "Front-left tire pressure began dropping 1 PSI per day." },
        { title: "Issue Logged", timestamp: "Oct 21, 2026 • 08:30 AM", description: "Alert generated for manual inspection." }
      ]
    }
  ] as IssueRecord[]
};
