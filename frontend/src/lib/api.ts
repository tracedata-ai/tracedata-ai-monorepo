export type BackendHealth = {
  status: "ok" | "mock";
  baseUrl: string;
  payload: Record<string, unknown>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
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
    const payload = await apiGet<Record<string, unknown>>("/health");
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
