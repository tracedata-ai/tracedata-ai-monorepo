export type BackendHealth = {
  status: "ok" | "mock";
  baseUrl: string;
  payload: Record<string, unknown>;
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

export type Trip = {
  id: string;
  tenant_id: string;
  vehicle_id: string;
  driver_id: string;
  route_id: string;
  status: string;
  created_at: string;
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

async function apiGet<T>(path: string): Promise<T> {
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
