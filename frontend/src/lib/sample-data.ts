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
