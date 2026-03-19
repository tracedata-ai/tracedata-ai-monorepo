"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { dashboardRows, type DashboardRow } from "@/lib/sample-data";

const columns: ColumnDef<DashboardRow>[] = [
  { accessorKey: "routeName", header: "Route" },
  { accessorKey: "activeTrips", header: "Active Trips" },
  {
    accessorKey: "avgRiskScore",
    header: "Avg Risk Score",
    cell: ({ row }) => row.original.avgRiskScore.toFixed(2),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status;
      const className =
        status === "Critical"
          ? "bg-red-600 hover:bg-red-700"
          : status === "Watch"
            ? "bg-amber-500 hover:bg-amber-600"
            : "bg-emerald-600 hover:bg-emerald-700";

      return <Badge className={className}>{status}</Badge>;
    },
  },
];

export default function DashboardPage() {
  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Active Routes</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">3</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">Live Trips</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">13</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium">
              Open Safety Issues
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-semibold">7</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Route Health Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={dashboardRows} />
        </CardContent>
      </Card>
    </div>
  );
}
