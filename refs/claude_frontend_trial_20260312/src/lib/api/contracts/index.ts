import type { Agent, OrchestrationEvent } from "../schemas/agent.schema";
import type { Driver } from "../schemas/driver.schema";
import type { Trip } from "../schemas/trip.schema";
import type { Route } from "../schemas/route.schema";
import type { Vehicle } from "../schemas/vehicle.schema";
import type { Issue } from "../schemas/issue.schema";
import type { Report } from "../schemas/report.schema";

// Shared response envelope
export type ApiMeta = {
  total: number;
  timestamp: string;
};

export type ListResponse<T> = { data: T[]; meta: ApiMeta };
export type SingleResponse<T> = { data: T; meta: { timestamp: string } };
export type ErrorResponse = { error: string; code: string; timestamp: string };

// --- Agent Contracts ---
// GET /api/agents
export type ListAgentsResponse = ListResponse<Agent>;
// GET /api/agents/feed
export type ListOrchestrationFeedResponse = ListResponse<OrchestrationEvent>;

// --- Driver Contracts ---
// GET /api/drivers
export type ListDriversResponse = ListResponse<Driver>;
// GET /api/drivers/[id]
export type GetDriverResponse = SingleResponse<Driver>;

// --- Trip Contracts ---
// GET /api/trips
export type ListTripsResponse = ListResponse<Trip>;
// GET /api/trips/[id]
export type GetTripResponse = SingleResponse<Trip>;

// --- Route Contracts ---
// GET /api/routes
export type ListRoutesResponse = ListResponse<Route>;
// GET /api/routes/[id]
export type GetRouteResponse = SingleResponse<Route>;

// --- Fleet (Vehicle) Contracts ---
// GET /api/fleet
export type ListFleetResponse = ListResponse<Vehicle>;
// GET /api/fleet/[id]
export type GetVehicleResponse = SingleResponse<Vehicle>;

// --- Issue Contracts ---
// GET /api/issues
export type ListIssuesResponse = ListResponse<Issue>;
// GET /api/issues/[id]
export type GetIssueResponse = SingleResponse<Issue>;

// --- Report Contracts ---
// GET /api/reports
export type ListReportsResponse = ListResponse<Report>;
