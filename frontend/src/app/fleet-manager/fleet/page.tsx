"use client";

import { useEffect, useRef, useState } from "react";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getVehicles, type Vehicle } from "@/lib/api";
import { FleetMap } from "@/components/maps/FleetMap";
import { VehicleCard } from "@/components/fleet/VehicleCard";
import { usePageAnimations } from "@/hooks/usePageAnimations";

type FleetRow = {
  id: string;
  licensePlate: string;
  model: string;
  status: string;
  lat: number;
  lng: number;
};

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
                    model: r.model,
                    status: r.status,
                    lat: r.lat,
                    lng: r.lng,
                  }))}
                />
              )}
            </CardContent>
          </Card>

          {/* Vehicle Registry Cards */}
          <Card className="glass rounded-xl animate-card">
            <CardHeader>
              <CardTitle>Vehicle Registry</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {Array.from({ length: 8 }).map((_, i) => (
                    <Skeleton key={i} className="h-64 w-full rounded-xl" />
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                  {rows.map((r, i) => (
                    <VehicleCard
                      key={r.id}
                      id={r.id}
                      licensePlate={r.licensePlate}
                      model={r.model}
                      status={r.status}
                      imageIndex={i}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </DashboardPageTemplate>
    </div>
  );
}
