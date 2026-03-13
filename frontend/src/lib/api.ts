/**
 * TraceData API Client
 * 
 * Provides a standardized way to interact with the FastAPI backend.
 * Handles base URL configuration and response parsing.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

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
  getDrivers: () => fetchApi<{ items: any[]; total: number }>("/entities/drivers"),
  getFleet: () => fetchApi<{ items: any[]; total: number }>("/entities/fleet"),
  getRoutes: () => fetchApi<{ items: any[]; total: number }>("/entities/routes"),
  getTrips: () => fetchApi<{ items: any[]; total: number }>("/entities/trips"),
  getIssues: () => fetchApi<{ items: any[]; total: number }>("/entities/issues"),
};
