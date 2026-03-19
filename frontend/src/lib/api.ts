export type BackendHealth = {
  status: "ok" | "mock";
  baseUrl: string;
  payload: Record<string, unknown>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API === "true";

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
export async function getVehicles(tenantId?: string): Promise<any[]> {
  const query = tenantId ? `?tenant_id=${tenantId}` : "";
  return apiGet<any[]>(`/fleet${query}`);
}

export async function getDrivers(tenantId?: string): Promise<any[]> {
  const query = tenantId ? `?tenant_id=${tenantId}` : "";
  return apiGet<any[]>(`/drivers${query}`);
}

export async function getTrips(tenantId?: string, status?: string): Promise<any[]> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (status) params.append("status", status);
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiGet<any[]>(`/trips${query}`);
}

export async function getIssues(tenantId?: string, tripId?: string): Promise<any[]> {
  const params = new URLSearchParams();
  if (tenantId) params.append("tenant_id", tenantId);
  if (tripId) params.append("trip_id", tripId);
  const query = params.toString() ? `?${params.toString()}` : "";
  return apiGet<any[]>(`/issues${query}`);
}

export async function getTenants(): Promise<any[]> {
  return apiGet<any[]>("/tenants");
}
