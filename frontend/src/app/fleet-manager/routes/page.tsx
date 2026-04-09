"use client";

import { useEffect, useState } from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { getRoutes, getTrips, type Route, type Trip } from "@/lib/api";
import { ColumnDef } from "@tanstack/react-table";
import { Skeleton } from "@/components/ui/skeleton";

type RouteRow = {
  id: string;
  routeName: string;
  origin: string;
  destination: string;
  distanceKm: number;
  activeDrivers: number;
};

const columns: ColumnDef<RouteRow>[] = [
  {
    accessorKey: "routeName",
    header: "Route Name",
    size: 150,
  },
  {
    accessorKey: "origin",
    header: "Origin",
    size: 120,
  },
  {
    accessorKey: "destination",
    header: "Destination",
    size: 120,
  },
  {
    accessorKey: "distanceKm",
    header: "Distance (km)",
    size: 100,
  },
  {
    accessorKey: "activeDrivers",
    header: "Active Drivers",
    size: 120,
  },
];

export default function RoutesPage() {
  const [rows, setRows] = useState<RouteRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadRoutes() {
      try {
        const [routes, trips] = await Promise.all([getRoutes(), getTrips()]);
        const activeTrips = trips.filter((t: Trip) => t.status === "active");
        const mapped = routes.map((r: Route) => {
          const routeTripCount = activeTrips.filter((t) => t.route_id === r.id).length;
          return {
            id: r.id,
            routeName: r.name,
            origin: r.start_location,
            destination: r.end_location,
            distanceKm: Number(r.distance_km ?? 0),
            activeDrivers: routeTripCount,
          };
        });
        setRows(mapped);
      } catch (error) {
        console.error("Failed to fetch routes:", error);
      } finally {
        setLoading(false);
      }
    }
    loadRoutes();
  }, []);

  const avgDistance =
    rows.length > 0 ? (rows.reduce((acc, row) => acc + row.distanceKm, 0) / rows.length).toFixed(1) : "0.0";
  const stats = [
    { label: "Total Routes", value: loading ? "..." : rows.length.toString(), change: 1 },
    { label: "Avg Distance", value: loading ? "..." : `${avgDistance} km`, change: 2 },
    { label: "Active Drivers", value: loading ? "..." : rows.reduce((acc, row) => acc + row.activeDrivers, 0).toString(), change: 1 },
  ];

  return (
    <DashboardPageTemplate
      title="Routes"
      subtitle="Manage planned corridors and logistics networks"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Route Registry</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <DataTable columns={columns} data={rows} />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
