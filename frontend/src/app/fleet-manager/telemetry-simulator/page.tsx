"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { DataTable } from "@/components/data-table";
import { telemetrySeedRows, type TelemetryEventRow } from "@/lib/sample-data";
import { ColumnDef } from "@tanstack/react-table";
import { useState } from "react";

const columns: ColumnDef<TelemetryEventRow>[] = [
  {
    accessorKey: "vehicleId",
    header: "Vehicle ID",
    size: 120,
  },
  {
    accessorKey: "speedKph",
    header: "Speed (kph)",
    size: 110,
  },
  {
    accessorKey: "harshBrakeCount",
    header: "Harsh Brakes",
    size: 120,
  },
  {
    accessorKey: "location",
    header: "Location",
    size: 140,
  },
  {
    accessorKey: "emittedAt",
    header: "Timestamp",
    size: 160,
  },
];

export default function TelemetrySimulatorPage() {
  const [events, setEvents] = useState(telemetrySeedRows);

  const handleEmitEvent = () => {
    const newEvent: TelemetryEventRow = {
      id: `evt-${Date.now()}`,
      vehicleId: `SGX-${Math.floor(2000 + Math.random() * 400)}`,
      speedKph: Math.floor(40 + Math.random() * 40),
      harshBrakeCount: Math.floor(Math.random() * 3),
      location: `1.${Math.floor(3000 + Math.random() * 500)}, 103.${Math.floor(8000 + Math.random() * 500)}`,
      emittedAt: new Date().toISOString().replace("T", " ").slice(0, 19),
    };

    setEvents((prev) => [newEvent, ...prev].slice(0, 50));
  };

  return (
    <DashboardPageTemplate
      title="Telemetry Simulator"
      subtitle="Emit and monitor real-time telemetry events"
    >
      <Card className="glass rounded-xl">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Telemetry Event Emitter</CardTitle>
          <Button
            onClick={handleEmitEvent}
            className="bg-[var(--info)] text-white hover:bg-[hsl(210_100%_45%)]"
          >
            Emit Event
          </Button>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={events} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
