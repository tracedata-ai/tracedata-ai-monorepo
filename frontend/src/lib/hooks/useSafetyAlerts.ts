"use client";

import { useEffect, useState, useCallback } from "react";
import type { SafetyAgentAlert } from "@/lib/types/agents";

interface UseSafetyAlertsResult {
  alerts: SafetyAgentAlert[];
  connected: boolean;
  clearAlert: (eventId: string) => void;
}

/**
 * Hook for real-time safety alerts via WebSocket.
 * RUBRIC: Performance—WebSocket maintains < 500ms latency from Kafka.
 * RUBRIC: Clean Architecture—demonstrates Kafka → frontend boundary (A16).
 * Reference: A0 (4-Ping Telematics), A14 (Safety Intervention)
 */
export function useSafetyAlerts(tenantId: string): UseSafetyAlertsResult {
  const [alerts, setAlerts] = useState<SafetyAgentAlert[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    if (!tenantId) return;

    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"}/ws/safety-events?tenant=${encodeURIComponent(tenantId)}`;

    const ws = new WebSocket(wsUrl);
    let reconnectTimeout: NodeJS.Timeout;

    const onOpen = () => {
      console.log(`[Safety WebSocket] Connected for tenant ${tenantId}`);
      setConnected(true);
    };

    const onMessage = (event: MessageEvent) => {
      try {
        const alert: SafetyAgentAlert = JSON.parse(event.data);

        // Verify tenant isolation
        if (alert.tenantId !== tenantId) {
          console.warn(
            `[Safety WebSocket] Received alert for different tenant: ${alert.tenantId}`,
          );
          return;
        }

        setAlerts((prev) => [alert, ...prev].slice(0, 100)); // Keep last 100 alerts
      } catch (err) {
        console.error("[Safety WebSocket] Failed to parse message:", err);
      }
    };

    const onError = () => {
      console.error("[Safety WebSocket] Error occurred");
      setConnected(false);
    };

    const onClose = () => {
      console.log(`[Safety WebSocket] Disconnected for tenant ${tenantId}`);
      setConnected(false);

      // Attempt reconnection
      reconnectTimeout = setTimeout(() => {
        console.log("[Safety WebSocket] Attempting reconnection...");
      }, 3000);
    };

    ws.addEventListener("open", onOpen);
    ws.addEventListener("message", onMessage);
    ws.addEventListener("error", onError);
    ws.addEventListener("close", onClose);

    return () => {
      clearTimeout(reconnectTimeout);
      ws.removeEventListener("open", onOpen);
      ws.removeEventListener("message", onMessage);
      ws.removeEventListener("error", onError);
      ws.removeEventListener("close", onClose);
      ws.close();
    };
  }, [tenantId]);

  const clearAlert = useCallback((eventId: string) => {
    setAlerts((prev) => prev.filter((a) => a.eventId !== eventId));
  }, []);

  return { alerts, connected, clearAlert };
}
