"use client";

import { useCallback, useState } from "react";

interface UseAgentQueryResult<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  mutate: (payload: unknown) => Promise<void>;
}

/**
 * Hook for querying the Orchestrator Agent.
 * RUBRIC: Clean Architecture—abstracts agent boundary via HTTP.
 * Reference: A1 (Orchestrator Agent)
 */
export function useAgentQuery<T>(endpoint: string): UseAgentQueryResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const mutate = useCallback(
    async (payload: unknown) => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem("token") || "";
        const tenantId = localStorage.getItem("tenantId") || "";

        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
            "x-tenant-id": tenantId,
          },
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          throw new Error(`Agent query failed: ${response.statusText}`);
        }

        const result: T = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
      } finally {
        setLoading(false);
      }
    },
    [endpoint],
  );

  return { data, loading, error, mutate };
}
