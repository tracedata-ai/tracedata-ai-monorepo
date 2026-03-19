"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { tripRows, type TripRow } from "@/lib/sample-data";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";

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

export default function TripsPage() {
  const stats = [
    { label: "Active Trips", value: "2", change: 1 },
    { label: "Delayed Trips", value: "1", change: 0 },
    { label: "Completed", value: "1", change: 1 },
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
          <DataTable columns={columns} data={tripRows} />
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
