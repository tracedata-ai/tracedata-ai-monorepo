// --- Types from Zod Schemas (single source of truth) ---
// Re-export for backwards compatibility with existing page imports
export type { AgentStatus, AgentType, AgentLastAction, Agent as AgentPulseData, OrchestrationEvent } from "@/lib/api/schemas/agent.schema";
export type { XaiExplanation, TripHistoryEntry, Driver as DriverProfile, DriverStatus, LicenseStatus } from "@/lib/api/schemas/driver.schema";
export type { TripStatus, TelemetrySegment, Trip as TripRecord } from "@/lib/api/schemas/trip.schema";
export type { Route as RouteRecord, RouteStatus } from "@/lib/api/schemas/route.schema";
export type { Vehicle as VehicleProfile, VehicleStatus, SignalStrength } from "@/lib/api/schemas/vehicle.schema";
export type { IssuePriority, IssueStatus, IssueTimelineEvent, Issue as IssueRecord } from "@/lib/api/schemas/issue.schema";

import type { Agent } from "@/lib/api/schemas/agent.schema";
import type { Driver } from "@/lib/api/schemas/driver.schema";
import type { Trip } from "@/lib/api/schemas/trip.schema";
import type { Route } from "@/lib/api/schemas/route.schema";
import type { Vehicle } from "@/lib/api/schemas/vehicle.schema";
import type { Issue } from "@/lib/api/schemas/issue.schema";
import type { OrchestrationEvent } from "@/lib/api/schemas/agent.schema";

// Legacy types still referenced by some page components
export interface MetricIndex {
  label: string;
  value: number;
  trend: number;
}

export interface BurnoutForecastNode {
  hourOffset: number;
  sectorId: string;
  riskLevel: number;
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

  // Agents — enriched with lastAction, confidenceScore, latencyMs
  agents: [
    {
      id: "AG-01", name: "Ingestion Quality", type: "Governance", status: "Active", loadPercentage: 45,
      description: "Deterministic telemetry scrubbing and routing.",
      lastAction: { message: "Scrubbed telemetry batch TRP-10042 (14 segments)", timestamp: "Just Now" },
      confidenceScore: 0.99, latencyMs: 42,
    },
    {
      id: "AG-02", name: "PII Scrubber", type: "Governance", status: "Active", loadPercentage: 12,
      description: "Sanitizes driver text inputs for privacy.",
      lastAction: { message: "Redacted PII from appeal submission app-3", timestamp: "3 mins ago" },
      confidenceScore: 1.0, latencyMs: 18,
    },
    {
      id: "AG-03", name: "Orchestrator", type: "Orchestration", status: "Active", loadPercentage: 88,
      description: "Central LangGraph dispatcher for all events.",
      lastAction: { message: "Dispatched Safety escalation for IDX-772 to Action tier", timestamp: "1 min ago" },
      confidenceScore: 0.97, latencyMs: 120,
    },
    {
      id: "AG-04", name: "Behavior", type: "Analysis", status: "Active", loadPercentage: 92,
      description: "End-of-Trip scoring and AIF360 fairness auditing.",
      lastAction: { message: "Scored TRP-10044 (94/100) — Nurul Huda, RT-003-A", timestamp: "8 mins ago" },
      confidenceScore: 0.93, latencyMs: 340,
    },
    {
      id: "AG-05", name: "Sentiment", type: "Analysis", status: "Idle", loadPercentage: 0,
      description: "Tracks emotional trajectory and burnout risk.",
      lastAction: { message: "Burnout heatmap export completed (REP-991)", timestamp: "2 hrs ago" },
      confidenceScore: 0.87, latencyMs: 0,
    },
    {
      id: "AG-06", name: "Context", type: "Analysis", status: "Active", loadPercentage: 25,
      description: "MCP-based enrichment (Weather, Road links).",
      lastAction: { message: "Elevated IDX-844 priority — monsoon warning in CBD zone", timestamp: "14 mins ago" },
      confidenceScore: 0.91, latencyMs: 210,
    },
    {
      id: "AG-07", name: "Safety", type: "Action", status: "Warning", loadPercentage: 30,
      description: "Real-time harsh event alerts and intervention.",
      lastAction: { message: "Halted charge cycle — IDX-772 thermal spike on VEH-4501", timestamp: "1 min ago" },
      confidenceScore: 0.98, latencyMs: 60,
    },
    {
      id: "AG-08", name: "Advocacy", type: "Action", status: "Active", loadPercentage: 78,
      description: "Processes driver appeals and disputes.",
      lastAction: { message: "Opened appeal app-1 review for TR-8291 (Route Efficiency Penalty)", timestamp: "5 mins ago" },
      confidenceScore: 0.85, latencyMs: 180,
    },
    {
      id: "AG-09", name: "Coaching", type: "Action", status: "Active", loadPercentage: 65,
      description: "Synthesizes XAI into personalized feedback.",
      lastAction: { message: "Generated feedback plan for TR-3310 (Rapid Acceleration pattern in CBD)", timestamp: "6 mins ago" },
      confidenceScore: 0.90, latencyMs: 250,
    },
  ] as Agent[],

  equilibrium: {
    safetyIndex: { label: "Safety Index", value: 90, trend: 2 },
    fairnessIndex: { label: "Fairness Index", value: 80, trend: -1 },
    sentimentTrend: 12,
    sentimentHistory: [60, 75, 55, 80, 70, 85, 90]
  },

  // Orchestration feed — now references real driver/issue/trip IDs
  orchestrationFeed: [
    {
      id: "evt-1", agentId: "AG-07", agentName: "Safety",
      message: "Halted charge cycle — thermal spike detected on VEH-4501 (IDX-772).",
      timestamp: "Just Now", severity: "error",
      relatedEntityId: "IDX-772", relatedEntityType: "issue",
    },
    {
      id: "evt-2", agentId: "AG-03", agentName: "Orchestrator",
      message: "Dispatched Context Agent to evaluate brake wear on VEH-8712 ahead of monsoon (IDX-844).",
      timestamp: "4 mins ago", severity: "warning",
      relatedEntityId: "IDX-844", relatedEntityType: "issue",
    },
    {
      id: "evt-3", agentId: "AG-09", agentName: "Coaching",
      message: "Generated personalised feedback plan for TR-3310 (Chen Wei Ming) — Rapid Acceleration in CBD.",
      timestamp: "6 mins ago", severity: "info",
      relatedEntityId: "TR-3310", relatedEntityType: "driver",
    },
    {
      id: "evt-4", agentId: "AG-04", agentName: "Behavior",
      message: "Scored TRP-10044 at 94/100 — TR-9922 (Nurul Huda) exemplary braking on RT-003-A.",
      timestamp: "8 mins ago", severity: "info",
      relatedEntityId: "TRP-10044", relatedEntityType: "trip",
    },
    {
      id: "evt-5", agentId: "AG-08", agentName: "Advocacy",
      message: "Opened dispute review for TR-8291 (Lim Wei Jie) — Route Efficiency Penalty appeal.",
      timestamp: "12 mins ago", severity: "info",
      relatedEntityId: "TR-8291", relatedEntityType: "driver",
    },
  ] as OrchestrationEvent[],

  appeals: [
    { id: "app-1", driverName: "Lim Wei Jie", driverId: "TR-8291", driverAvatarUrl: "https://ui-avatars.com/api/?name=Lim+Wei+Jie&background=f87171&color=fff", reason: "Route Efficiency Penalty", priority: "Urgent", status: "Pending Review" },
    { id: "app-2", driverName: "Siti Aisyah", driverId: "TR-4512", driverAvatarUrl: "https://ui-avatars.com/api/?name=Siti+Aisyah&background=fcd34d&color=000", reason: "Break Schedule Alert", priority: "Medium", status: "Pending Review" },
    { id: "app-3", driverName: "Muthu Kumar", driverId: "TR-0114", driverAvatarUrl: "https://ui-avatars.com/api/?name=Muthu+Kumar&background=94a3b8&color=fff", reason: "Inactivity Flag Dispute", priority: "Low", status: "Pending Review" },
  ] as AppealContest[],

  drivers: [
    {
      id: "TR-8291", name: "Lim Wei Jie", status: "Active", tripsCompleted: 14, rating: 4.8,
      avgTripScore: 92, licenseStatus: "Valid", recentIncidents: 0,
      explanation: {
        humanSummary: "Professional and cautious driver with exceptional speed adherence. Maintains steady pace even in Changi's high-traffic zones.",
        featureImportance: { "Speed Adherence": 0.25, "Harsh Braking": 0.15, "Rapid Acceleration": 0.12, "Cornering G-Force": 0.10, "Idling Duration": 0.08, "Routing Efficiency": 0.07, "Eco-Driving Score": 0.07, "Fatigue Indicators": 0.06, "Following Distance": 0.05, "Signal Compliance": 0.05 },
        fairnessAuditScore: 0.12
      },
      tripHistory: [
        { tripId: "TRP-10020", score: 88, date: "2026-03-01T08:00:00Z" },
        { tripId: "TRP-10025", score: 92, date: "2026-03-03T10:00:00Z" },
        { tripId: "TRP-10030", score: 90, date: "2026-03-05T09:00:00Z" },
        { tripId: "TRP-10035", score: 85, date: "2026-03-07T14:30:00Z" },
        { tripId: "TRP-10040", score: 94, date: "2026-03-09T11:00:00Z" },
        { tripId: "TRP-10042", score: 92, date: "2026-03-11T08:30:00Z" },
      ]
    },
    {
      id: "TR-4512", name: "Siti Aisyah", status: "On Break", tripsCompleted: 22, rating: 4.9,
      avgTripScore: 96, licenseStatus: "Valid", recentIncidents: 0,
      explanation: {
        humanSummary: "High-consistency safe driving profile. Demonstrates superior route optimization and fuel efficiency.",
        featureImportance: { "Eco-Driving Score": 0.20, "Routing Efficiency": 0.18, "Speed Adherence": 0.15, "Following Distance": 0.12, "Harsh Braking": 0.10, "Signal Compliance": 0.08, "Cornering G-Force": 0.06, "Idling Duration": 0.05, "Rapid Acceleration": 0.04, "Fatigue Indicators": 0.02 },
        fairnessAuditScore: 0.08
      },
      tripHistory: [
        { tripId: "TRP-09010", score: 95, date: "2026-02-15T07:00:00Z" },
        { tripId: "TRP-09015", score: 97, date: "2026-02-20T12:00:00Z" },
        { tripId: "TRP-09020", score: 94, date: "2026-02-25T08:00:00Z" },
        { tripId: "TRP-09025", score: 96, date: "2026-03-02T16:00:00Z" },
        { tripId: "TRP-10043", score: 98, date: "2026-03-11T10:15:00Z" },
      ]
    },
    {
      id: "TR-0114", name: "Muthu Kumar", status: "Off Duty", tripsCompleted: 12, rating: 4.5,
      avgTripScore: 88, licenseStatus: "Expiring Soon", recentIncidents: 1,
      explanation: {
        humanSummary: "Performance dip identified during night shifts due to steering micro-corrections (Fatigue). Safety remains above baseline.",
        featureImportance: { "Fatigue Indicators": -0.15, "Speed Adherence": 0.12, "Idling Duration": 0.12, "Following Distance": 0.10, "Routing Efficiency": 0.10, "Signal Compliance": 0.10, "Harsh Braking": 0.08, "Cornering G-Force": 0.08, "Rapid Acceleration": 0.08, "Eco-Driving Score": 0.07 },
        fairnessAuditScore: 0.15
      },
      tripHistory: [
        { tripId: "TRP-12001", score: 92, date: "2026-03-01T22:00:00Z" },
        { tripId: "TRP-12005", score: 85, date: "2026-03-03T23:30:00Z" },
        { tripId: "TRP-12010", score: 82, date: "2026-03-05T01:00:00Z" },
        { tripId: "TRP-12015", score: 88, date: "2026-03-07T21:00:00Z" },
        { tripId: "TRP-12020", score: 90, date: "2026-03-10T19:00:00Z" },
      ]
    },
    {
      id: "TR-9922", name: "Nurul Huda", status: "Active", tripsCompleted: 8, rating: 5.0,
      avgTripScore: 98, licenseStatus: "Valid", recentIncidents: 0,
      explanation: {
        humanSummary: "Perfect adherence to IMDA safe-driving guidelines. Exemplary use of indicators and following distance.",
        featureImportance: { "Speed Adherence": 0.15, "Signal Compliance": 0.15, "Following Distance": 0.15, "Eco-Driving Score": 0.12, "Harsh Braking": 0.10, "Rapid Acceleration": 0.10, "Cornering G-Force": 0.08, "Routing Efficiency": 0.05, "Idling Duration": 0.05, "Fatigue Indicators": 0.05 },
        fairnessAuditScore: 0.05
      },
      tripHistory: [
        { tripId: "TRP-10041", score: 98, date: "2026-03-10T09:00:00Z" },
        { tripId: "TRP-10044", score: 94, date: "2026-03-11T05:00:00Z" },
      ]
    },
    {
      id: "TR-3310", name: "Chen Wei Ming", status: "Active", tripsCompleted: 26, rating: 4.7,
      avgTripScore: 85, licenseStatus: "Expired", recentIncidents: 2,
      explanation: {
        humanSummary: "Aggressive acceleration profile detected in urban CBD sectors. Recommended for eco-driving modules.",
        featureImportance: { "Rapid Acceleration": -0.20, "Speed Adherence": 0.12, "Harsh Braking": 0.10, "Routing Efficiency": 0.10, "Cornering G-Force": 0.10, "Following Distance": 0.08, "Eco-Driving Score": 0.08, "Signal Compliance": 0.08, "Idling Duration": 0.07, "Fatigue Indicators": 0.07 },
        fairnessAuditScore: 0.18
      },
      tripHistory: [
        { tripId: "TRP-10010", score: 85, date: "2026-03-01T12:00:00Z" },
        { tripId: "TRP-10015", score: 82, date: "2026-03-03T13:00:00Z" },
        { tripId: "TRP-10020", score: 88, date: "2026-03-05T14:00:00Z" },
        { tripId: "TRP-10025", score: 84, date: "2026-03-07T15:00:00Z" },
        { tripId: "TRP-10030", score: 86, date: "2026-03-09T16:00:00Z" },
      ]
    },
  ] as Driver[],

  routes: [
    { id: "RT-001-A", name: "Changi to CBD Express", origin: "Changi Airport T3", destination: "Marina Bay Sands", historicalAvgMins: 30, standardDistanceKm: 19.5, totalTripsCompleted: 542, status: "Active" },
    { id: "RT-001-B", name: "CBD to Changi Express", origin: "Marina Bay Sands", destination: "Changi Airport T3", historicalAvgMins: 25, standardDistanceKm: 19.5, totalTripsCompleted: 500, status: "Active" },
    { id: "RT-002-A", name: "Sentosa Inbound", origin: "VivoCity", destination: "Sentosa Cove", historicalAvgMins: 15, standardDistanceKm: 8.0, totalTripsCompleted: 4200, status: "Active" },
    { id: "RT-002-B", name: "Sentosa Outbound", origin: "Sentosa Cove", destination: "VivoCity", historicalAvgMins: 18, standardDistanceKm: 8.0, totalTripsCompleted: 4350, status: "Active" },
    { id: "RT-003-A", name: "East Coast Park Outbound", origin: "Bedok Mall", destination: "East Coast Park", historicalAvgMins: 10, standardDistanceKm: 4.2, totalTripsCompleted: 215, status: "Active" },
    { id: "RT-003-B", name: "East Coast Park Return", origin: "East Coast Park", destination: "Bedok Mall", historicalAvgMins: 12, standardDistanceKm: 4.2, totalTripsCompleted: 215, status: "Active" },
    { id: "RT-004-A", name: "Mandai Wildlife Transfer", origin: "Boon Lay MRT", destination: "Mandai Wildlife Reserve", historicalAvgMins: 25, standardDistanceKm: 15.8, totalTripsCompleted: 110, status: "Active" },
    { id: "RT-004-B", name: "Mandai City Return", origin: "Mandai Wildlife Reserve", destination: "Boon Lay MRT", historicalAvgMins: 22, standardDistanceKm: 15.8, totalTripsCompleted: 100, status: "Active" },
  ] as Route[],

  trips: [
    {
      id: "TRP-10042", vehicleId: "V-991", driverId: "TR-8291", routeId: "RT-001-A",
      status: "In Progress", startTime: "2026-03-11T08:30:00Z",
      historicalAvgMins: 30, actualDurationMins: 35, distanceKm: 19.5, currentDistanceKm: 12.0,
    },
    {
      id: "TRP-10043", vehicleId: "V-228", driverId: "TR-4512", routeId: "RT-002-B",
      status: "In Progress", startTime: "2026-03-11T10:15:00Z",
      historicalAvgMins: 18, actualDurationMins: 12, distanceKm: 8.0, currentDistanceKm: 6.5,
    },
    {
      id: "TRP-10044", vehicleId: "V-045", driverId: "TR-9922", routeId: "RT-003-A",
      status: "Completed", startTime: "2026-03-11T05:00:00Z",
      historicalAvgMins: 10, actualDurationMins: 10, distanceKm: 4.2, currentDistanceKm: 4.2,
      score: 94, nationalSpeedLimit: 90,
      explanation: {
        humanSummary: "Exemplary safety execution. Proactive braking and generous following distance mitigated congestion risks.",
        featureImportance: { "Following Distance": 0.20, "Harsh Braking": 0.15, "Speed Adherence": 0.15, "Eco-Driving Score": 0.10, "Signal Compliance": 0.10, "Idling Duration": 0.10, "Routing Efficiency": 0.05, "Cornering G-Force": 0.05, "Rapid Acceleration": 0.05, "Fatigue Indicators": 0.05 },
        fairnessAuditScore: 0.04
      },
      telemetrySegments: [
        { timestamp: "05:00:00", speed: 0, brakePressure: 0, throttlePos: 0, isSafeZone: true },
        { timestamp: "05:01:00", speed: 30, brakePressure: 0, throttlePos: 40, isSafeZone: true, rewardType: "Smooth Launch" },
        { timestamp: "05:02:00", speed: 50, brakePressure: 0, throttlePos: 20, isSafeZone: true },
        { timestamp: "05:03:00", speed: 60, brakePressure: 0, throttlePos: 15, isSafeZone: true, rewardType: "Steady Cruise" },
        { timestamp: "05:04:00", speed: 55, brakePressure: 10, throttlePos: 0, isSafeZone: true, rewardType: "Proactive Braking" },
        { timestamp: "05:05:00", speed: 40, brakePressure: 0, throttlePos: 30, isSafeZone: true },
        { timestamp: "05:06:00", speed: 45, brakePressure: 0, throttlePos: 20, isSafeZone: true, rewardType: "Safe Lane Change" },
        { timestamp: "05:07:00", speed: 50, brakePressure: 0, throttlePos: 15, isSafeZone: true },
        { timestamp: "05:08:00", speed: 60, brakePressure: 0, throttlePos: 10, isSafeZone: true, rewardType: "Eco-Modulation" },
        { timestamp: "05:09:00", speed: 30, brakePressure: 40, throttlePos: 0, isSafeZone: true, rewardType: "Controlled Stop" },
        { timestamp: "05:10:00", speed: 0, brakePressure: 0, throttlePos: 0, isSafeZone: true }
      ]
    },
    {
      id: "TRP-10045", vehicleId: "V-712", driverId: "TR-3310", routeId: "RT-004-B",
      status: "Scheduled", startTime: "2026-03-11T14:00:00Z",
      historicalAvgMins: 22, distanceKm: 15.8, currentDistanceKm: 0,
      // Causal link: Coaching Agent flagged TR-3310 before this upcoming trip
      agentEventId: "evt-3",
    },
  ] as Trip[],

  vehicles: [
    { id: "VEH-8712", plateNumber: "SGB-1234M", model: "EV-Transit Pro", status: "In Transit", operatingHours: 1250, driver: "Lim Wei Jie", location: "Marina Bay Sands", signal: "Strong" },
    { id: "VEH-4501", plateNumber: "SGB-5678X", model: "EV-Transit Pro", status: "Charging", operatingHours: 840, driver: "Siti Aisyah", location: "Changi Terminal 3, EV Bay", signal: "Strong" },
    { id: "VEH-9923", plateNumber: "SGC-9012K", model: "Heavy Hauler 500", status: "Maintenance", operatingHours: 3420, driver: "Muthu Kumar", location: "Jurong West Depot", signal: "Weak" },
    { id: "VEH-1102", plateNumber: "SGB-3456P", model: "EV-Transit Pro", status: "Idle", operatingHours: 150, driver: "Nurul Huda", location: "Woodlands Checkpoint", signal: "Strong" },
    { id: "VEH-3345", plateNumber: "SGB-9876R", model: "EV-Transit Pro", status: "In Transit", operatingHours: 420, driver: "Chen Wei Ming", location: "CTE (Central Expressway)", signal: "Medium" },
  ] as Vehicle[],

  issues: [
    {
      id: "IDX-902", vehicleId: "VEH-9923", assetName: "Heavy Hauler 500",
      priority: "Critical", type: "Engine", summary: "Overheating",
      agent: "Safety Agent", status: "Resolved",
      reportedDate: "Oct 24, 2026", resolvedDate: "Oct 25, 2026 at 10:30 AM",
      technician: "Mike Repairs (Jurong West Depot)",
      resolutionAction: "Radiator replaced and coolant system flushed.",
      agentReasoning: "Safety Agent flagged this as critical based on sensor data showing oil temperature exceeding 220°F while at idle. Correlated with driver logs indicating 'odd noise' at stop-and-go intervals.",
      agentTags: ["Engine Thermals", "Acoustic Signal"],
      relatedDriverId: "TR-0114",
      timeline: [
        { title: "Issue Detected", timestamp: "Oct 24, 2026 • 08:42 AM", description: "Automatic diagnostic scan triggered fault code P0217." },
        { title: "AI Analysis Completed", timestamp: "Oct 24, 2026 • 08:45 AM", description: "Safety Agent assigned priority 'Critical' based on route history." },
        { title: "Dispatched to Maintenance", timestamp: "Oct 24, 2026 • 09:15 AM", description: "Assigned to Jurong West Depot Service Team." }
      ]
    },
    {
      id: "IDX-844", vehicleId: "VEH-8712", assetName: "EV-Transit Pro",
      priority: "High", type: "Brakes", summary: "Wear Alert",
      agent: "Context Agent", status: "Open",
      reportedDate: "Oct 23, 2026",
      agentReasoning: "Context Agent correlated weather data (heavy rain expected in CBD) with deteriorating brake pad sensors (under 15% life). High risk of hydroplaning or extended stopping distance.",
      agentTags: ["Weather Context", "Sensor Telemetry"],
      relatedDriverId: "TR-8291",
      timeline: [
        { title: "Sensor Threshold Reached", timestamp: "Oct 23, 2026 • 02:14 PM", description: "Brake pad wear sensor below 15%." },
        { title: "Context Agent Evaluation", timestamp: "Oct 23, 2026 • 02:18 PM", description: "Priority elevated to 'High' due to impending monsoon warning in service area." }
      ]
    },
    {
      id: "IDX-772", vehicleId: "VEH-4501", assetName: "EV-Transit Pro",
      priority: "High", type: "Battery", summary: "Thermal Spike",
      agent: "Safety Agent", status: "Open",
      reportedDate: "Oct 22, 2026",
      agentReasoning: "Safety Agent detected rapid temperature escalation in Cell Block 4 during fast-charging at Changi Terminal 3. Halting charge cycle to prevent thermal runaway.",
      agentTags: ["Battery Thermals", "Charge Cycle"],
      relatedDriverId: "TR-4512",
      timeline: [
        { title: "Temp Anomaly Detected", timestamp: "Oct 22, 2026 • 11:30 AM", description: "Cell Block 4 temp exceeded 45°C during active charging." },
        { title: "Charge Logic Interrupted", timestamp: "Oct 22, 2026 • 11:31 AM", description: "Safety Agent terminated charge session." }
      ]
    },
    {
      id: "IDX-104", vehicleId: "VEH-1102", assetName: "EV-Transit Pro",
      priority: "Medium", type: "Tires", summary: "Low PSI",
      agent: "Maintenance Agent", status: "Open",
      reportedDate: "Oct 21, 2026",
      agentReasoning: "Maintenance Agent noted a slow 3 PSI drop over 48 hours on the front-left tire while operating near Woodlands Checkpoint. Likely a slow leak.",
      agentTags: ["TPMS Data", "Gradual Variance"],
      relatedDriverId: "TR-9922",
      timeline: [
        { title: "Pressure Drop Flagged", timestamp: "Oct 19, 2026 • 09:00 AM", description: "Front-left tire pressure began dropping 1 PSI per day." },
        { title: "Issue Logged", timestamp: "Oct 21, 2026 • 08:30 AM", description: "Alert generated for manual inspection." }
      ]
    }
  ] as Issue[],
};
