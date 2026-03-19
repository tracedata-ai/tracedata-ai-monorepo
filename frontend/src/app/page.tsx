"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/shared/DataTable";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
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
    <DashboardPageTemplate
      title="Dashboard"
      subtitle="Live command center for fleet health, routing, and safety operations."
      stats={[
        { label: "Active Routes", value: 3, change: 8 },
        { label: "Live Trips", value: 13, change: 5 },
        { label: "Open Safety Issues", value: 7, change: -3 },
      ]}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle className="text-base font-bold uppercase tracking-tight">
            Route Health Overview
          </CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={dashboardRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
