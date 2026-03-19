"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { tripRows, type TripRow } from "@/lib/sample-data";

const columns: ColumnDef<TripRow>[] = [
  { accessorKey: "id", header: "Trip ID" },
  { accessorKey: "driver", header: "Driver" },
  { accessorKey: "routeName", header: "Route" },
  { accessorKey: "startedAt", header: "Start Time" },
  { accessorKey: "etaMinutes", header: "ETA (mins)" },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status;
      const variant = status === "Delayed" ? "destructive" : "secondary";
      return <Badge variant={variant}>{status}</Badge>;
    },
  },
];

export default function TripsPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Trips</CardTitle>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={tripRows} />
      </CardContent>
    </Card>
  );
}
