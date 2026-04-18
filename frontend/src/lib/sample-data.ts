export type DashboardRow = {
  id: string;
  routeName: string;
  activeTrips: number;
  avgRiskScore: number;
  status: "Healthy" | "Watch" | "Critical";
};

export type RouteRow = {
  id: string;
  routeName: string;
  origin: string;
  destination: string;
  distanceKm: number;
  activeDrivers: number;
};

export type TripRow = {
  id: string;
  driver: string;
  routeName: string;
  startedAt: string;
  etaMinutes: number;
  status: "In Transit" | "Delayed" | "Completed";
};

export type DriverRow = {
  id: string;
  name: string;
  assignedRoute: string;
  hoursToday: number;
  fatigueRisk: "Low" | "Medium" | "High";
};

export type IssueRow = {
  id: string;
  severity: "Low" | "Medium" | "High";
  category: "Fatigue" | "Overspeed" | "Device Offline" | "Route Deviation";
  driver: string;
  routeName: string;
  createdAt: string;
};

export type TelemetryEventRow = {
  id: string;
  vehicleId: string;
  speedKph: number;
  harshBrakeCount: number;
  location: string;
  emittedAt: string;
};

export const dashboardRows: DashboardRow[] = [
  {
    id: "dash-1",
    routeName: "Port Loop Alpha",
    activeTrips: 6,
    avgRiskScore: 0.18,
    status: "Healthy",
  },
  {
    id: "dash-2",
    routeName: "Northern Cargo Link",
    activeTrips: 4,
    avgRiskScore: 0.42,
    status: "Watch",
  },
  {
    id: "dash-3",
    routeName: "City Hub Express",
    activeTrips: 3,
    avgRiskScore: 0.71,
    status: "Critical",
  },
];

export const routeRows: RouteRow[] = [
  {
    id: "route-1",
    routeName: "Port Loop Alpha",
    origin: "Jurong Port",
    destination: "Tuas Depot",
    distanceKm: 28,
    activeDrivers: 6,
  },
  {
    id: "route-2",
    routeName: "Northern Cargo Link",
    origin: "Woodlands Yard",
    destination: "Changi Cargo",
    distanceKm: 41,
    activeDrivers: 4,
  },
  {
    id: "route-3",
    routeName: "City Hub Express",
    origin: "City Hub",
    destination: "Bukit Timah Node",
    distanceKm: 19,
    activeDrivers: 3,
  },
];

export const tripRows: TripRow[] = [
  {
    id: "trip-7842",
    driver: "Farid Rahman",
    routeName: "Port Loop Alpha",
    startedAt: "2026-03-19 07:20",
    etaMinutes: 24,
    status: "In Transit",
  },
  {
    id: "trip-7843",
    driver: "Alicia Tan",
    routeName: "Northern Cargo Link",
    startedAt: "2026-03-19 07:05",
    etaMinutes: 46,
    status: "Delayed",
  },
  {
    id: "trip-7844",
    driver: "Marcus Lee",
    routeName: "City Hub Express",
    startedAt: "2026-03-19 06:10",
    etaMinutes: 0,
    status: "Completed",
  },
];

export const driverRows: DriverRow[] = [
  {
    id: "drv-103",
    name: "Farid Rahman",
    assignedRoute: "Port Loop Alpha",
    hoursToday: 4.2,
    fatigueRisk: "Low",
  },
  {
    id: "drv-117",
    name: "Alicia Tan",
    assignedRoute: "Northern Cargo Link",
    hoursToday: 8.1,
    fatigueRisk: "High",
  },
  {
    id: "drv-122",
    name: "Marcus Lee",
    assignedRoute: "City Hub Express",
    hoursToday: 6.3,
    fatigueRisk: "Medium",
  },
];

export const issueRows: IssueRow[] = [
  {
    id: "iss-501",
    severity: "High",
    category: "Fatigue",
    driver: "Alicia Tan",
    routeName: "Northern Cargo Link",
    createdAt: "2026-03-19 07:31",
  },
  {
    id: "iss-502",
    severity: "Medium",
    category: "Overspeed",
    driver: "Farid Rahman",
    routeName: "Port Loop Alpha",
    createdAt: "2026-03-19 07:14",
  },
  {
    id: "iss-503",
    severity: "Low",
    category: "Device Offline",
    driver: "Marcus Lee",
    routeName: "City Hub Express",
    createdAt: "2026-03-19 06:58",
  },
];

export const telemetrySeedRows: TelemetryEventRow[] = [
  {
    id: "evt-001",
    vehicleId: "SGX-2210",
    speedKph: 56,
    harshBrakeCount: 0,
    location: "1.3005, 103.8000",
    emittedAt: "2026-03-19 07:40:12",
  },
  {
    id: "evt-002",
    vehicleId: "SGX-2141",
    speedKph: 68,
    harshBrakeCount: 1,
    location: "1.3301, 103.8412",
    emittedAt: "2026-03-19 07:41:03",
  },
];

/** 10-minute 1Hz batch — edge stats only; aligns with backend `common/samples/smoothness_batch.py`. */
export type SmoothnessBatchDetails = {
  sample_count: number;
  window_seconds: number;
  speed: {
    mean_kmh: number;
    std_dev: number;
    max_kmh: number;
    variance: number;
  };
  longitudinal: {
    mean_accel_g: number;
    std_dev: number;
    max_decel_g: number;
    harsh_brake_count: number;
    harsh_accel_count: number;
  };
  lateral: {
    mean_lateral_g: number;
    max_lateral_g: number;
    harsh_corner_count: number;
  };
  jerk: { mean: number; max: number; std_dev: number };
  engine: {
    mean_rpm: number;
    max_rpm: number;
    idle_seconds: number;
    idle_events: number;
    longest_idle_seconds: number;
    over_rev_count: number;
    over_rev_seconds: number;
  };
  incident_event_ids: string[];
  raw_log_url: string;
};

export const smoothnessLogBatchDetailsSample: SmoothnessBatchDetails = {
  sample_count: 600,
  window_seconds: 600,
  speed: {
    mean_kmh: 72.3,
    std_dev: 8.1,
    max_kmh: 94.0,
    variance: 65.6,
  },
  longitudinal: {
    mean_accel_g: 0.04,
    std_dev: 0.12,
    max_decel_g: -0.31,
    harsh_brake_count: 0,
    harsh_accel_count: 0,
  },
  lateral: {
    mean_lateral_g: 0.02,
    max_lateral_g: 0.18,
    harsh_corner_count: 0,
  },
  jerk: { mean: 0.008, max: 0.041, std_dev: 0.006 },
  engine: {
    mean_rpm: 1820,
    max_rpm: 2340,
    idle_seconds: 45,
    idle_events: 1,
    longest_idle_seconds: 38,
    over_rev_count: 0,
    over_rev_seconds: 0,
  },
  incident_event_ids: ["DEV-HB-002", "DEV-SPD-006"],
  raw_log_url: "s3://tracedata-sensors/T12345-batch-20260307-1010.bin",
};

// ── Coaching mock data ────────────────────────────────────────────────────────

export type CoachingEntry = {
  driverId: string;
  driverName: string;
  category: string;
  priority: "high" | "medium" | "low";
  message: string;
  created_at: string;
};

export const coachingQueue: CoachingEntry[] = [
  { driverId: "drv-117", driverName: "Alicia Tan",   category: "fatigue_management", priority: "high",   message: "Driver exceeded 8 h continuous operation. Mandatory rest stop required before next dispatch.", created_at: "2026-04-17T22:10:00Z" },
  { driverId: "drv-117", driverName: "Alicia Tan",   category: "harsh_braking",      priority: "high",   message: "3 harsh-brake events on Northern Cargo Link. Review deceleration technique.",               created_at: "2026-04-17T20:45:00Z" },
  { driverId: "drv-122", driverName: "Marcus Lee",   category: "overspeed",          priority: "medium", message: "Average speed 12 kph over limit on two City Hub segments. Speed-awareness module recommended.", created_at: "2026-04-17T19:30:00Z" },
  { driverId: "drv-103", driverName: "Farid Rahman", category: "route_deviation",    priority: "medium", message: "Unexplained 4-min deviation from Port Loop Alpha waypoints. Debrief recommended.",            created_at: "2026-04-17T18:00:00Z" },
  { driverId: "drv-122", driverName: "Marcus Lee",   category: "idle_time",          priority: "low",    message: "Engine idled 22 min during scheduled route. Review pre-departure checklist.",                created_at: "2026-04-16T14:20:00Z" },
  { driverId: "drv-103", driverName: "Farid Rahman", category: "fuel_efficiency",    priority: "low",    message: "Fuel consumption 8% above baseline. Eco-driving refresher suggested.",                       created_at: "2026-04-16T11:05:00Z" },
];
