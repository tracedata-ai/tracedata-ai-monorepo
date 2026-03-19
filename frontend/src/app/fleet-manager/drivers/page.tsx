"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { driverRows, type DriverRow } from "@/lib/sample-data";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";

const columns: ColumnDef<DriverRow>[] = [
  {
    accessorKey: "name",
    header: "Driver Name",
    size: 150,
  },
  {
    accessorKey: "assignedRoute",
    header: "Assigned Route",
    size: 160,
  },
  {
    accessorKey: "hoursToday",
    header: "Hours Today",
    cell: (info) => `${(info.getValue() as number).toFixed(1)} h`,
    size: 110,
  },
  {
    accessorKey: "fatigueRisk",
    header: "Fatigue Risk",
    cell: (info) => {
      const level = info.getValue() as string;
      const variant =
        {
          Low: "bg-[var(--success)]",
          Medium: "bg-[var(--warning)]",
          High: "bg-[var(--error)]",
        }[level] || "bg-gray-500";

      return <Badge className={`${variant} text-white`}>{level}</Badge>;
    },
    size: 120,
  },
];

export default function DriversPage() {
  const stats = [
    { label: "Total Drivers", value: driverRows.length, change: 1 },
    { label: "High Fatigue", value: "1", change: -1 },
    { label: "Avg Hours", value: "6.2 h", change: 0 },
  ];

  return (
    <DashboardPageTemplate
      title="Drivers"
      subtitle="Monitor driver performance, safety, and fatigue levels"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Driver Roster</CardTitle>
        </CardHeader>
        <CardContent>
          <DataTable columns={columns} data={driverRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
