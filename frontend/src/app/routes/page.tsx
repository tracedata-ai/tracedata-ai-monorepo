"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table";
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
    <Card>
      <CardHeader>
        <CardTitle>Routes</CardTitle>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={routeRows} />
      </CardContent>
    </Card>
  );
}
