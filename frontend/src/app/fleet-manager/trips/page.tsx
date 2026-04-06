"use client";

import { useEffect, useState } from "react";
import { getWorkflowTrips, type WorkflowTrip } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const columns: ColumnDef<TripRow>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
    size: 100,
  },
  {
    accessorKey: "routeName",
    header: "Route",
    size: 140,
  },
  {
    accessorKey: "driver",
    header: "Driver",
    size: 130,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const status = info.getValue() as string;
      const variant =
        {
          "In Transit": "bg-[var(--info)]",
          Completed: "bg-[var(--success)]",
          Delayed: "bg-[var(--warning)]",
        }[status] || "bg-gray-500";

      return <Badge className={`${variant} text-white`}>{status}</Badge>;
    },
    size: 110,
  },
  {
    accessorKey: "startedAt",
    header: "Start Time",
    size: 140,
  },
  {
    accessorKey: "etaMinutes",
    header: "ETA (min)",
    size: 110,
  },
];

type TripRow = {
  id: string;
  driver: string;
  routeName: string;
  startedAt: string;
  etaMinutes: number;
  status: "In Transit" | "Delayed" | "Completed";
};

export default function TripsPage() {
  const [trips, setTrips] = useState<TripRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTrips() {
      try {
        const tripsData = await getWorkflowTrips();
        const now = Date.now();
        const mapped: TripRow[] = tripsData.map((t: WorkflowTrip) => {
          const started = new Date(t.started_at || t.updated_at || new Date().toISOString());
          const minutesRunning = Math.max(
            0,
            Math.floor((now - started.getTime()) / 60000)
          );
          return ({
          id: t.trip_id.slice(0, 12),
          routeName: t.truck_id,
          driver: t.driver_id,
          status: t.status === "active" ? "In Transit" : "Completed",
          startedAt: started.toLocaleTimeString(),
          etaMinutes: t.status === "active" ? Math.max(5, 120 - minutesRunning) : 0,
        });
        });
        setTrips(mapped);
      } catch (error) {
        console.error("Failed to fetch trips:", error);
      } finally {
        setLoading(false);
      }
    }
    loadTrips();
  }, []);

  const stats = [
    { label: "Active Trips", value: loading ? "..." : trips.filter(t => t.status === "In Transit").length.toString(), change: 1 },
    { label: "Completed", value: loading ? "..." : trips.filter(t => t.status === "Completed").length.toString(), change: 1 },
  ];

  return (
    <DashboardPageTemplate
      title="Trips"
      subtitle="Monitor ongoing and historical trip data"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Trip Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <DataTable columns={columns} data={trips} />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
