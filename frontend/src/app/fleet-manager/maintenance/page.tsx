"use client";

import { useEffect, useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getMaintenance, getVehicles, type Maintenance, type Vehicle } from "@/lib/api";

type MaintenanceRow = {
  id: string;
  licensePlate: string;
  maintenanceType: string;
  status: string;
  triggeredBy: string;
  scheduledDate: string;
  createdAt: string;
};

const columns: ColumnDef<MaintenanceRow>[] = [
  { accessorKey: "licensePlate", header: "Vehicle" },
  { accessorKey: "maintenanceType", header: "Type" },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const status = String(info.getValue() ?? "");
      const cls =
        status === "completed"
          ? "bg-[var(--success)]"
          : status === "overdue"
            ? "bg-[var(--error)]"
            : "bg-[var(--warning)]";
      return <Badge className={`${cls} text-white`}>{status}</Badge>;
    },
  },
  { accessorKey: "triggeredBy", header: "Triggered By" },
  { accessorKey: "scheduledDate", header: "Scheduled" },
  { accessorKey: "createdAt", header: "Created" },
];

export default function MaintenancePage() {
  const [rows, setRows] = useState<MaintenanceRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMaintenance() {
      try {
        const [maintenance, vehicles] = await Promise.all([getMaintenance(), getVehicles()]);
        const vehicleById = new Map(vehicles.map((v: Vehicle) => [v.id, v]));
        setRows(
          maintenance.map((m: Maintenance) => ({
            id: m.id,
            licensePlate: vehicleById.get(m.vehicle_id)?.license_plate ?? m.vehicle_id.slice(0, 8),
            maintenanceType: m.maintenance_type,
            status: m.status,
            triggeredBy: m.triggered_by,
            scheduledDate: m.scheduled_date ?? "—",
            createdAt: new Date(m.created_at).toLocaleString(),
          }))
        );
      } finally {
        setLoading(false);
      }
    }
    loadMaintenance();
  }, []);

  const stats = [
    { label: "Records", value: loading ? "..." : rows.length.toString(), change: 1 },
    {
      label: "Safety Triggered",
      value: loading ? "..." : rows.filter((r) => r.triggeredBy === "safety_agent").length.toString(),
      change: 1,
    },
  ];

  return (
    <DashboardPageTemplate
      title="Maintenance"
      subtitle="Maintenance records and AI-triggered actions"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Maintenance Records</CardTitle>
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
