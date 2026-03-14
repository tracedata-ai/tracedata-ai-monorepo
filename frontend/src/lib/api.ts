/**
 * TraceData API Client
 * 
 * Provides a standardized way to interact with the FastAPI backend.
 * Handles base URL configuration and response parsing.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

/**
 * Shared Entity Interfaces
 */
/**
 * Shared Backend Entity Interfaces (Matching Python models)
 */
export interface BackendDriver {
  id: string;
  first_name: string;
  last_name: string;
  license_number: string;
  phone_number: string;
  status: string;
  avatar?: string;
}

export interface BackendVehicle {
  id: string;
  vin: string;
  license_plate: string;
  make: string;
  model: string;
  year: string;
  status: string;
}

export interface BackendRoute {
  id: string;
  name: string;
  start_location: string;
  end_location: string;
  estimated_distance: number;
  estimated_duration: number;
}

export interface BackendTrip {
  id: string;
  vehicle_id: string;
  driver_id: string;
  route_id: string;
  status: string;
  start_time: string;
  end_time?: string;
  actual_distance?: number;
  safety_score?: number;
}

export interface BackendIssue {
  id: string;
  vehicle_id: string;
  trip_id?: string;
  issue_type: string;
  severity: string;
  description: string;
  status: string;
}

export interface TelemetryPayload {
  event_id: string;
  event_type: string;
  trip_id: string;
  driver_id: string;
  timestamp: string;
  details: Record<string, string | number | boolean | null>;
}

export interface ChatPayload {
  message: string;
}

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(errorData.detail || `API Request failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Entity-specific API calls
 */
export const entitiesApi = {
  getDrivers: () => fetchApi<{ items: BackendDriver[]; total: number }>("/driver-wellness/drivers"),
  getFleet: () => fetchApi<{ items: BackendVehicle[]; total: number }>("/telemetry-safety/fleet"),
  getRoutes: () => fetchApi<{ items: BackendRoute[]; total: number }>("/telemetry-safety/routes"),
  getTrips: () => fetchApi<{ items: BackendTrip[]; total: number }>("/telemetry-safety/trips"),
  getIssues: () => fetchApi<{ items: BackendIssue[]; total: number }>("/telemetry-safety/issues"),
};

export const telemetryApi = {
  ingest: (payload: TelemetryPayload) => fetchApi("/telemetry-safety/telemetry", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
};

export const agentsApi = {
  chat: (payload: ChatPayload) => fetchApi("/orchestration/chat-shell", {
    method: "POST",
    body: JSON.stringify(payload),
  }),
};
