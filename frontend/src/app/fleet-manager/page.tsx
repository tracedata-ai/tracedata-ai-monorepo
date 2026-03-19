"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { dashboardRows, type DashboardRow } from "@/lib/sample-data";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";

const columns: ColumnDef<DashboardRow>[] = [
  {
    accessorKey: "routeName",
    header: "Route Name",
    size: 150,
  },
  {
    accessorKey: "activeTrips",
    header: "Active Trips",
    size: 110,
  },
  {
    accessorKey: "avgRiskScore",
    header: "Avg Risk Score",
    cell: (info) => (info.getValue() as number).toFixed(2),
    size: 120,
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const status = info.getValue() as string;
      const badgeVariant =
        {
          Healthy: "bg-[var(--success)]",
          Watch: "bg-[var(--warning)]",
          Critical: "bg-[var(--error)]",
        }[status] || "bg-[var(--info)]";

      return <Badge className={`${badgeVariant} text-white`}>{status}</Badge>;
    },
    size: 100,
  },
];

export default function FleetManagerDashboard() {
  const stats = [
    { label: "Active Routes", value: "3", change: 1 },
    { label: "Active Trips", value: "13", change: 2 },
    { label: "Avg Risk", value: "0.44", change: -3 },
  ];

  return (
    <DashboardPageTemplate
      title="Fleet Dashboard"
      subtitle="Real-time monitoring of routes, drivers, and fleet health"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Route Performance Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={dashboardRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
