"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/shared/DataTable";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { routeRows, type RouteRow } from "@/lib/sample-data";

const columns: ColumnDef<RouteRow>[] = [
  { accessorKey: "routeName", header: "Route" },
  { accessorKey: "origin", header: "Origin" },
  { accessorKey: "destination", header: "Destination" },
  { accessorKey: "distanceKm", header: "Distance (km)" },
  { accessorKey: "activeDrivers", header: "Active Drivers" },
];

export default function RoutesPage() {
  return (
    <DashboardPageTemplate
      title="Routes"
      subtitle="Monitor planned corridors, distance, and driver assignment load."
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle className="text-base font-bold uppercase tracking-tight">
            Route Registry
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={routeRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
