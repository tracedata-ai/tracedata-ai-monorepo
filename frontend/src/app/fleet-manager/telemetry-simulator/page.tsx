"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/data-table";
import {
  emitTelemetrySimulatorEvent,
  runSimulatorBatch,
  type SimulatorEventKind,
} from "@/lib/api";
import { ColumnDef } from "@tanstack/react-table";
import { useMemo, useState } from "react";

type SimulatorLogRow = {
  id: string;
  kind: SimulatorEventKind;
  tripId: string;
  truckId: string;
  driverId: string;
  eventTypes: string;
  emittedAt: string;
  status: "ok" | "error";
};

const columns: ColumnDef<SimulatorLogRow>[] = [
  {
    accessorKey: "kind",
    header: "Event Kind",
    size: 120,
  },
  {
    accessorKey: "tripId",
    header: "Trip ID",
    size: 120,
  },
  {
    accessorKey: "eventTypes",
    header: "Event Type(s)",
    size: 140,
  },
  {
    accessorKey: "emittedAt",
    header: "Timestamp",
    size: 160,
  },
];

export default function TelemetrySimulatorPage() {
  const [tripId, setTripId] = useState(`TRP-UI-${Date.now()}`);
  const [truckId, setTruckId] = useState("T12345");
  const [driverId, setDriverId] = useState("DRV-ANON-7829");
  const [sending, setSending] = useState<SimulatorEventKind | null>(null);
  const [batchRunning, setBatchRunning] = useState(false);
  const [batchResult, setBatchResult] = useState<string | null>(null);
  const [events, setEvents] = useState<SimulatorLogRow[]>([]);

  const actions = useMemo(
    () =>
      [
        { kind: "start", label: "Send Start" },
        { kind: "harsh", label: "Send Harsh" },
        { kind: "smooth", label: "Send Smooth" },
        { kind: "feedback", label: "Send Feedback" },
        { kind: "end", label: "Send End Trip" },
      ] as const,
    []
  );

  const handleEmitEvent = async (kind: SimulatorEventKind) => {
    setSending(kind);
    try {
      const result = await emitTelemetrySimulatorEvent({
        kind,
        trip_id: tripId,
        truck_id: truckId,
        driver_id: driverId,
      });
      const newEvent: SimulatorLogRow = {
        id: `evt-${Date.now()}`,
        kind,
        tripId,
        truckId,
        driverId,
        eventTypes: result.event_types.join(", "),
        emittedAt: new Date().toISOString().replace("T", " ").slice(0, 19),
        status: "ok",
      };
      setEvents((prev) => [newEvent, ...prev].slice(0, 50));
    } catch {
      const failed: SimulatorLogRow = {
        id: `err-${Date.now()}`,
        kind,
        tripId,
        truckId,
        driverId,
        eventTypes: "—",
        emittedAt: new Date().toISOString().replace("T", " ").slice(0, 19),
        status: "error",
      };
      setEvents((prev) => [failed, ...prev].slice(0, 50));
    } finally {
      setSending(null);
    }
  };

  const resetTrip = () => {
    setTripId(`TRP-UI-${Date.now()}`);
  };

  const handleBatchRun = async () => {
    setBatchRunning(true);
    setBatchResult(null);
    try {
      const result = await runSimulatorBatch({
        truck_count: 10,
        event_delay: 2.0,
        truck_delay: 5.0,
      });
      setBatchResult(
        `Started: ${result.truck_count} trucks · ~${result.estimated_duration_seconds}s estimated`
      );
    } catch {
      setBatchResult("Failed to start batch run.");
    } finally {
      setBatchRunning(false);
    }
  };

  return (
    <DashboardPageTemplate
      title="Telemetry Simulator"
      subtitle="Send workflow events directly from UI"
    >
      <Card className="glass rounded-xl">
        <CardHeader className="space-y-3">
          <CardTitle>Full Cycle Simulator</CardTitle>
          <p className="text-sm text-muted-foreground">
            Run a complete trip cycle (start → harsh → smooth → feedback → end)
            for 10 trucks with gradual time intervals. Events are spaced 2s
            apart; trucks stagger by 5s.
          </p>
          <div className="flex items-center gap-3">
            <Button
              onClick={handleBatchRun}
              disabled={batchRunning}
              className="bg-[var(--success,#16a34a)] text-white hover:bg-green-700 disabled:opacity-60"
            >
              {batchRunning ? "Running…" : "Run Full Cycle (10 trucks)"}
            </Button>
            {batchResult && (
              <span className="text-sm text-muted-foreground">{batchResult}</span>
            )}
          </div>
        </CardHeader>
      </Card>

      <Card className="glass rounded-xl">
        <CardHeader className="space-y-3">
          <CardTitle>Telemetry Event Emitter</CardTitle>
          <div className="grid gap-2 md:grid-cols-3">
            <input
              value={tripId}
              onChange={(e) => setTripId(e.target.value)}
              placeholder="Trip ID"
              className="rounded-md border border-[#e5e7eb] px-3 py-2 text-sm"
            />
            <input
              value={truckId}
              onChange={(e) => setTruckId(e.target.value)}
              placeholder="Truck ID"
              className="rounded-md border border-[#e5e7eb] px-3 py-2 text-sm"
            />
            <input
              value={driverId}
              onChange={(e) => setDriverId(e.target.value)}
              placeholder="Driver ID"
              className="rounded-md border border-[#e5e7eb] px-3 py-2 text-sm"
            />
          </div>
          <div className="flex flex-wrap gap-2">
            {actions.map((action) => (
              <Button
                key={action.kind}
                onClick={() => handleEmitEvent(action.kind)}
                disabled={!!sending}
                className="bg-[var(--info)] text-white hover:bg-[hsl(210_100%_45%)] disabled:opacity-60"
              >
                {sending === action.kind ? "Sending..." : action.label}
              </Button>
            ))}
            <Button variant="outline" onClick={resetTrip}>
              New Trip ID
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={events} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
