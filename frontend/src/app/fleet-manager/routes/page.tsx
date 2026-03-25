"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { routeRows, type RouteRow } from "@/lib/sample-data";
import { ColumnDef } from "@tanstack/react-table";

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
  const stats = [
    { label: "Total Routes", value: routeRows.length, change: 1 },
    { label: "Avg Distance", value: "29.3 km", change: 2 },
    { label: "Active Drivers", value: "13", change: 1 },
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
          <DataTable columns={columns} data={routeRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
