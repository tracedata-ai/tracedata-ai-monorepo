export type BackendHealth = {
  status: "ok" | "mock";
  baseUrl: string;
  payload: Record<string, unknown>;
};

export type AgentFlowEvent = {
  event_type: "agent_queued" | "agent_running" | "agent_done" | "worker_health";
  status:
    | "idle"
    | "queued"
    | "running"
    | "success"
    | "error"
    | "healthy"
    | "degraded"
    | "unhealthy";
  agent: "orchestrator" | "safety" | "scoring" | "sentiment" | "support";
  seq: number;
  ts: string;
  trip_id?: string | null;
  meta?: Record<string, unknown>;
};

export type AgentFlowSnapshot = {
  seq: number;
  updated_at: string;
  execution: Record<string, "idle" | "queued" | "running" | "success" | "error">;
  worker_health: Record<string, "healthy" | "degraded" | "unhealthy">;
  active_trip_id?: string | null;
};

export type SimulatorEventKind = "start" | "harsh" | "feedback" | "smooth" | "end";

export type SimulatorEmitResponse = {
  status: "ok";
  pushed_count: number;
  queue: string;
  emitted_kind: SimulatorEventKind;
  trip_id: string;
  truck_id: string;
  driver_id: string;
  event_types: string[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

export type Tenant = {
  id: string;
  name: string;
  contact_email: string;
  status: string;
};

export type Vehicle = {
  id: string;
  tenant_id: string;
  license_plate: string;
  model: string;
  status: string;
};

export type Driver = {
  id: string;
  tenant_id: string;
  first_name: string;
  last_name: string;
  email: string;
  license_number: string;
  experience_level: string;
};

export type Route = {
  id: string;
  tenant_id: string;
  name: string;
  start_location: string;
  end_location: string;
  distance_km?: string | number | null;
  route_type: string;
  created_at: string;
};

export type Trip = {
  id: string;
  tenant_id: string;
  vehicle_id: string;
  driver_id: string;
  route_id: string;
  status: string;
  created_at: string;
};

export type Maintenance = {
  id: string;
  tenant_id: string;
  vehicle_id: string;
  maintenance_type: string;
  status: string;
  scheduled_date?: string | null;
  completed_date?: string | null;
  notes?: string | null;
  triggered_by: string;
  created_at: string;
};

export type WorkflowTrip = {
  trip_id: string;
  driver_id: string;
  truck_id: string;
  status: string;
  started_at?: string | null;
  updated_at?: string | null;
};

export type Issue = {
  id: string;
  tenant_id: string;
  trip_id: string;
  severity: string;
  category: string;
  event_type: string;
  description?: string;
  created_at: string;
};

export type SafetyEvent = {
  id: string;
  event_id: string;
  trip_id: string;
  event_type: string;
  severity: string;
  event_timestamp: string | null;
  lat: number | null;
  lon: number | null;
  traffic_conditions: string | null;
  weather_conditions: string | null;
  created_at: string | null;
  // decision fields
  decision_id: string | null;
  decision: string | null;
  action: string | null;
  reason: string | null;
  recommended_action: string | null;
  // from analysis JSONB
  assessed_severity: string | null;
  llm_path: boolean;
  analysis_reason: string | null;
  video_url: string | null;
  truck_id: string | null;
  driver_id: string | null;
  route_name: string | null;
  trip_started_at: string | null;
};

async function apiGet<T>(path: string): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }

    return (await response.json()) as T;
  } catch (error) {
    console.warn(`API call to ${path} failed, falling back to dummy data.`, error);
    
    // Map path to dummy data key
    let key = "";
    if (path.startsWith("/fleet")) key = "vehicles";
    else if (path.startsWith("/drivers")) key = "drivers";
    else if (path.startsWith("/trips")) key = "trips";
    else if (path.startsWith("/routes")) key = "routes";
    else if (path.startsWith("/issues")) key = "issues";
    else if (path.startsWith("/maintenance")) key = "maintenance";
    else if (path.startsWith("/tenants")) key = "tenants";
    
    if (key) {
      try {
        const fallbackResponse = await fetch('/data/dummy-data.json');
        if (!fallbackResponse.ok) throw new Error("Fallback file not found");
        const fallbackData = await fallbackResponse.json();
        let result = fallbackData[key] as T;
        
        // Simple filtering for tenant_id if present in query
        if (Array.isArray(result) && path.includes("tenant_id=")) {
          const params = new URLSearchParams(path.split("?")[1]);
          const tenantId = params.get("tenant_id");
          if (tenantId) {
            result = (result as Array<{ tenant_id?: string }>).filter((item) => item.tenant_id === tenantId) as unknown as T;
          }
        }
        return result;
      } catch (fallbackError) {
        console.error("Fallback failed:", fallbackError);
        throw error;
      }
    }
    throw error;
  }
}

async function apiPost<T>(path: string, payload: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function getBackendHealth(): Promise<BackendHealth> {
  const safeBaseUrl = API_BASE_URL || "mock://local";

  if (USE_MOCK_API || !API_BASE_URL) {
    return {
      status: "mock",
      baseUrl: safeBaseUrl,
      payload: {
        message: "Running with mock API",
        timestamp: new Date().toISOString(),
      },
    };
  }

  try {
    // Health check is at the root, not under /api/v1
    const rootUrl = API_BASE_URL.replace("/api/v1", "");
    const response = await fetch(`${rootUrl}/health`);
    if (!response.ok) throw new Error("Health check failed");
    const payload = await response.json();
    return {
      status: "ok",
      baseUrl: safeBaseUrl,
      payload,
    };
  } catch {
    return {
      status: "mock",
      baseUrl: safeBaseUrl,
      payload: {
        message: "Backend unreachable. Falling back to mock response.",
        timestamp: new Date().toISOString(),
      },
    };
  }
}

export async function getVehicles(tenantId?: string): Promise<Vehicle[]> {
  const query = tenantId ? `?tenant_id=${tenantId}` : "";
  return apiGet<Vehicle[]>(`/fleet${query}`);
}

export async function getDrivers(tenantId?: string): Promise<Driver[]> {
  const query = tenantId ? `?tenant_id=${tenantId}` : "";
  return apiGet<Driver[]>(`/drivers${query}`);
}

export async function getTrips(tenantId?: string, status?: string): Promise<Trip[]> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (status) params.append("status", status);
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiGet<Trip[]>(`/trips${query}`);
}

export async function getWorkflowTrips(status?: string): Promise<WorkflowTrip[]> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiGet<WorkflowTrip[]>(`/workflow/trips${query}`);
}

export async function getRoutes(tenantId?: string): Promise<Route[]> {
  const query = tenantId ? `?tenant_id=${tenantId}` : "";
  return apiGet<Route[]>(`/routes${query}`);
}

export async function getIssues(tenantId?: string, tripId?: string): Promise<Issue[]> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (tripId) params.append("trip_id", tripId);
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiGet<Issue[]>(`/issues${query}`);
}

export async function getTenants(): Promise<Tenant[]> {
  return apiGet<Tenant[]>("/tenants");
}

export async function getMaintenance(vehicleId?: string): Promise<Maintenance[]> {
  const query = vehicleId ? `?vehicle_id=${vehicleId}` : "";
  return apiGet<Maintenance[]>(`/maintenance${query}`);
}

export type TripDetail = {
  trip_id: string;
  status: string;
  created_at: string | null;
  driver_name: string | null;
  license_plate: string | null;
  vehicle: string | null;
  route_name: string | null;
  route_from: string | null;
  route_to: string | null;
  distance_km: number | null;
  scoring: {
    score: number | null;
    breakdown: Record<string, number>;
    narrative: string | null;
  };
  safety_events: Array<{
    event_id: string;
    event_type: string;
    severity: string;
    lat: number | null;
    lon: number | null;
    timestamp: string | null;
    traffic: string | null;
    weather: string | null;
    decision: string | null;
    action: string | null;
    reason: string | null;
    recommended_action: string | null;
  }>;
  coaching: Array<{
    category: string;
    priority: string;
    message: string;
  }>;
  sentiment: {
    score: number | null;
    label: string | null;
    emotions: Record<string, number>;
  } | null;
};

export async function getTripDetail(tripId: string): Promise<TripDetail> {
  return apiGet<TripDetail>(`/trips/${tripId}/detail`);
}

export async function getSafetyEvents(limit = 100): Promise<SafetyEvent[]> {
  return apiGet<SafetyEvent[]>(`/safety/events/?limit=${limit}`);
}

export async function getSafetyEvent(eventId: string): Promise<SafetyEvent> {
  return apiGet<SafetyEvent>(`/safety/events/${eventId}`);
}

type AgentFlowHandlers = {
  onSnapshot?: (snapshot: AgentFlowSnapshot) => void;
  onEvent: (event: AgentFlowEvent) => void;
  onError?: () => void;
};

export function connectAgentFlowStream(handlers: AgentFlowHandlers): EventSource {
  const rootUrl = API_BASE_URL.replace("/api/v1", "");
  const source = new EventSource(`${rootUrl}/api/v1/agent-flow/stream`);
  source.addEventListener("snapshot", (e) => {
    if (!handlers.onSnapshot) return;
    try {
      handlers.onSnapshot(JSON.parse((e as MessageEvent).data) as AgentFlowSnapshot);
    } catch {
      // Ignore malformed payloads to keep stream alive.
    }
  });
  source.addEventListener("agentflow", (e) => {
    try {
      handlers.onEvent(JSON.parse((e as MessageEvent).data) as AgentFlowEvent);
    } catch {
      // Ignore malformed payloads to keep stream alive.
    }
  });
  source.onerror = () => {
    handlers.onError?.();
  };
  return source;
}

export async function emitTelemetrySimulatorEvent(input: {
  kind: SimulatorEventKind;
  trip_id: string;
  truck_id: string;
  driver_id: string;
}): Promise<SimulatorEmitResponse> {
  return apiPost<SimulatorEmitResponse>("/simulator/emit", input);
}

export type SimulatorBatchResponse = {
  status: "started";
  truck_count: number;
  event_delay: number;
  truck_delay: number;
  estimated_duration_seconds: number;
};

export async function runSimulatorBatch(input: {
  truck_count?: number;
  event_delay?: number;
  truck_delay?: number;
}): Promise<SimulatorBatchResponse> {
  return apiPost<SimulatorBatchResponse>("/simulator/run-batch", input);
}
