"use client";

import { useEffect, useRef, useState } from "react";
import { type ColumnDef } from "@tanstack/react-table";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { getVehicles, type Vehicle } from "@/lib/api";
import { FleetMap } from "@/components/maps/FleetMap";
import { usePageAnimations } from "@/hooks/usePageAnimations";

type FleetRow = {
  id: string;
  licensePlate: string;
  model: string;
  status: string;
  lat: number;
  lng: number;
};

const columns: ColumnDef<FleetRow>[] = [
  { accessorKey: "licensePlate", header: "License Plate" },
  { accessorKey: "model", header: "Model" },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const status = String(info.getValue() ?? "");
      const color =
        status === "active"
          ? "bg-[var(--success)]"
          : status === "in_maintenance"
            ? "bg-[var(--error)]"
            : "bg-[var(--warning)]";
      return <Badge className={`${color} text-white`}>{status}</Badge>;
    },
  },
  { accessorKey: "id", header: "Vehicle ID" },
];

// Deterministic mock coordinates around Singapore for vehicles without GPS data
function mockCoords(index: number): { lat: number; lng: number } {
  const base = { lat: 1.3521, lng: 103.8198 };
  const offsets = [
    { lat: 0.02, lng: 0.05 },
    { lat: -0.01, lng: 0.03 },
    { lat: 0.04, lng: -0.02 },
    { lat: -0.03, lng: 0.06 },
    { lat: 0.01, lng: -0.04 },
    { lat: 0.06, lng: 0.01 },
    { lat: -0.02, lng: -0.03 },
    { lat: 0.03, lng: 0.07 },
  ];
  const o = offsets[index % offsets.length];
  return { lat: base.lat + o.lat, lng: base.lng + o.lng };
}

export default function FleetPage() {
  const [rows, setRows] = useState<FleetRow[]>([]);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  usePageAnimations(containerRef, ".animate-card");

  useEffect(() => {
    async function loadFleet() {
      try {
        const vehicles = await getVehicles();
        setRows(
          vehicles.map((v: Vehicle, i: number) => ({
            id: v.id.substring(0, 8),
            licensePlate: v.license_plate,
            model: v.model,
            status: v.status,
            ...mockCoords(i),
          })),
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
    {
      label: "In Maintenance",
      value: loading ? "..." : rows.filter((r) => r.status === "in_maintenance").length.toString(),
      change: 0,
    },
  ];

  return (
    <div ref={containerRef}>
      <DashboardPageTemplate title="Fleet" subtitle="Vehicle registry and status" stats={stats}>
        <div className="flex flex-col gap-4">
          {/* Map */}
          <Card className="glass rounded-xl animate-card">
            <CardHeader>
              <CardTitle>Live Positions</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-[360px] w-full" />
              ) : (
                <FleetMap
                  vehicles={rows.map((r) => ({
                    id: r.id,
                    licensePlate: r.licensePlate,
                    status: r.status,
                    lat: r.lat,
                    lng: r.lng,
                  }))}
                />
              )}
            </CardContent>
          </Card>

          {/* Vehicle Registry Table */}
          <Card className="glass rounded-xl animate-card">
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
                <DataTable
                  columns={columns}
                  data={rows}
                  searchPlaceholder="Search by plate, model, status..."
                />
              )}
            </CardContent>
          </Card>
        </div>
      </DashboardPageTemplate>
    </div>
  );
}
