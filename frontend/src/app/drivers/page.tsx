"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { driverRows, type DriverRow } from "@/lib/sample-data";

const columns: ColumnDef<DriverRow>[] = [
  { accessorKey: "id", header: "Driver ID" },
  { accessorKey: "name", header: "Name" },
  { accessorKey: "assignedRoute", header: "Assigned Route" },
  { accessorKey: "hoursToday", header: "Hours Today" },
  {
    accessorKey: "fatigueRisk",
    header: "Fatigue Risk",
    cell: ({ row }) => {
      const risk = row.original.fatigueRisk;
      const className =
        risk === "High"
          ? "bg-red-600 hover:bg-red-700"
          : risk === "Medium"
            ? "bg-amber-500 hover:bg-amber-600"
            : "bg-emerald-600 hover:bg-emerald-700";
      return <Badge className={className}>{risk}</Badge>;
    },
  },
];

export default function DriversPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Drivers</CardTitle>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={driverRows} />
      </CardContent>
    </Card>
  );
}
