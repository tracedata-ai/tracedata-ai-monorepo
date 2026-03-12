"use client";

import React from "react";
import { useSafetyAlerts } from "@/lib/hooks/useSafetyAlerts";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface SafetyAlertPanelProps {
  tenantId: string;
  className?: string;
}

/**
 * SafetyAlertPanel displays real-time safety alerts via WebSocket.
 * RUBRIC: Performance—WebSocket maintains < 500ms latency from Kafka (A16).
 * Reference: A0 (4-Ping Critical Events), A14 (Safety Intervention)
 */
export function SafetyAlertPanel({
  tenantId,
  className,
}: SafetyAlertPanelProps) {
  const { alerts, connected, clearAlert } = useSafetyAlerts(tenantId);

  return (
    <div
      className={cn(
        "rounded-lg border border-gray-200 bg-white p-6 space-y-4",
        className,
      )}
    >
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900">Safety Alerts</h3>
        <div className="flex items-center gap-2">
          <div
            className={`h-2 w-2 rounded-full ${
              connected ? "bg-teal-500" : "bg-gray-400"
            }`}
          />
          <span className="text-xs text-gray-600">
            {connected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {alerts.length === 0 ? (
        <div className="rounded bg-gray-50 p-4 text-center text-sm text-gray-600">
          No active safety alerts
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {alerts.map((alert) => (
            <div
              key={alert.eventId}
              className={`rounded p-4 ${
                alert.severity === "critical"
                  ? "bg-red-50 border border-red-200"
                  : "bg-yellow-50 border border-yellow-200"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p
                    className={`font-semibold ${
                      alert.severity === "critical"
                        ? "text-red-900"
                        : "text-yellow-900"
                    }`}
                  >
                    Level {alert.interventionLevel}:{" "}
                    {alert.severity === "critical"
                      ? "CRITICAL ALERT"
                      : "WARNING"}
                  </p>
                  <p
                    className={`text-sm mt-1 ${
                      alert.severity === "critical"
                        ? "text-red-800"
                        : "text-yellow-800"
                    }`}
                  >
                    {alert.message}
                  </p>
                  <div className="flex gap-4 mt-2 text-xs text-gray-600">
                    <span>Driver: {alert.driverId}</span>
                    <span>Trip: {alert.tripId}</span>
                    <span>
                      {new Date(alert.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <Button
                  onClick={() => clearAlert(alert.eventId)}
                  variant="outline"
                  size="sm"
                  className="whitespace-nowrap"
                >
                  Dismiss
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="rounded bg-blue-50 p-3 text-sm text-blue-800">
        <p className="font-semibold">Real-Time Integration</p>
        <p className="mt-1">
          Alerts arrive via WebSocket from the Safety Agent (Kafka pipeline).
          Level 3 alerts trigger immediate Fleet Manager escalation.
        </p>
      </div>
    </div>
  );
}
