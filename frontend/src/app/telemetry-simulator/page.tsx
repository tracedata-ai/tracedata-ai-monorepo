"use client";

import { useMemo, useState } from "react";
import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/shared/DataTable";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { telemetrySeedRows, type TelemetryEventRow } from "@/lib/sample-data";

const columns: ColumnDef<TelemetryEventRow>[] = [
  { accessorKey: "id", header: "Event ID" },
  { accessorKey: "vehicleId", header: "Vehicle ID" },
  { accessorKey: "speedKph", header: "Speed (kph)" },
  { accessorKey: "harshBrakeCount", header: "Harsh Brakes" },
  { accessorKey: "location", header: "Location" },
  { accessorKey: "emittedAt", header: "Emitted At" },
];

function randomInt(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export default function TelemetrySimulatorPage() {
  const [vehicleId, setVehicleId] = useState("SGX-2210");
  const [events, setEvents] = useState<TelemetryEventRow[]>(telemetrySeedRows);

  const totalEvents = useMemo(() => events.length, [events]);

  const emitEvent = () => {
    const now = new Date();
    const nextEvent: TelemetryEventRow = {
      id: `evt-${Math.random().toString(36).slice(2, 8)}`,
      vehicleId,
      speedKph: randomInt(35, 92),
      harshBrakeCount: randomInt(0, 3),
      location: `1.${randomInt(2900, 3600)}, 103.${randomInt(7600, 9200)}`,
      emittedAt: now.toISOString().replace("T", " ").slice(0, 19),
    };

    setEvents((prev) => [nextEvent, ...prev].slice(0, 12));
  };

  return (
    <DashboardPageTemplate
      title="Telemetry Simulator"
      subtitle="Mimic telematics device emissions before live backend ingestion."
      stats={[{ label: "Buffered Events", value: totalEvents }]}
    >
      <div className="space-y-4">
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-base font-bold uppercase tracking-tight">
              Event Generator
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="w-full sm:max-w-xs">
              <label className="mb-1 block text-sm font-medium text-muted-foreground">
                Vehicle ID
              </label>
              <Input
                value={vehicleId}
                onChange={(event) =>
                  setVehicleId(event.target.value.toUpperCase())
                }
                placeholder="SGX-2210"
              />
            </div>
            <Button
              className="bg-[var(--info)] text-white hover:bg-[hsl(210_100%_45%)]"
              onClick={emitEvent}
            >
              Emit Telemetry Event
            </Button>
            <p className="text-sm font-semibold text-muted-foreground">
              Buffered events: {totalEvents}
            </p>
          </CardContent>
        </Card>

        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-base font-bold uppercase tracking-tight">
              Recent Emissions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              columns={columns}
              data={events}
              emptyMessage="No telemetry events yet."
            />
          </CardContent>
        </Card>
      </div>
    </DashboardPageTemplate>
  );
}
