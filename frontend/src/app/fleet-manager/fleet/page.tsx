"use client";

import { useEffect, useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getVehicles, type Vehicle } from "@/lib/api";

type FleetRow = {
  id: string;
  licensePlate: string;
  model: string;
  status: string;
};

const columns: ColumnDef<FleetRow>[] = [
  { accessorKey: "licensePlate", header: "License Plate" },
  { accessorKey: "model", header: "Model" },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const status = String(info.getValue() ?? "");
      const color = status === "active" ? "bg-[var(--success)]" : "bg-[var(--warning)]";
      return <Badge className={`${color} text-white`}>{status}</Badge>;
    },
  },
  { accessorKey: "id", header: "Vehicle ID" },
];

export default function FleetPage() {
  const [rows, setRows] = useState<FleetRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadFleet() {
      try {
        const vehicles = await getVehicles();
        setRows(
          vehicles.map((v: Vehicle) => ({
            id: v.id.substring(0, 8),
            licensePlate: v.license_plate,
            model: v.model,
            status: v.status,
          }))
        );
      } finally {
        setLoading(false);
      }
    }
    loadFleet();
  }, []);

  const stats = [
    { label: "Total Vehicles", value: loading ? "..." : rows.length.toString(), change: 1 },
    {
      label: "Active",
      value: loading ? "..." : rows.filter((r) => r.status === "active").length.toString(),
      change: 1,
    },
  ];

  return (
    <DashboardPageTemplate title="Fleet" subtitle="Vehicle registry and status" stats={stats}>
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Vehicle Registry</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <DataTable columns={columns} data={rows} />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
