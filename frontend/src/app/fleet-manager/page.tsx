"use client";

import { useEffect, useRef, useState } from "react";
import { getVehicles, getTrips } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { VehicleStatusChart } from "@/components/charts/VehicleStatusChart";
import { TripStatusChart } from "@/components/charts/TripStatusChart";
import { usePageAnimations } from "@/hooks/usePageAnimations";

export default function FleetManagerDashboard() {
  const [fleetCount, setFleetCount] = useState<number | null>(null);
  const [activeTrips, setActiveTrips] = useState<number | null>(null);
  const [vehicleStatuses, setVehicleStatuses] = useState({ active: 0, inactive: 0, inMaintenance: 0 });
  const [tripStatuses, setTripStatuses] = useState<{ label: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  usePageAnimations(containerRef, ".animate-card");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [vehicles, trips] = await Promise.all([
          getVehicles(),
          getTrips(),
        ]);
        setFleetCount(vehicles.length);
        setActiveTrips(trips.filter((t) => t.status === "active" || t.status === "in_transit").length);

        setVehicleStatuses({
          active: vehicles.filter((v) => v.status === "active").length,
          inactive: vehicles.filter((v) => v.status === "inactive").length,
          inMaintenance: vehicles.filter((v) => v.status === "in_maintenance").length,
        });

        const statusCounts = trips.reduce<Record<string, number>>((acc, t) => {
          acc[t.status] = (acc[t.status] ?? 0) + 1;
          return acc;
        }, {});
        setTripStatuses(
          Object.entries(statusCounts).map(([label, count]) => ({ label, count })),
        );
      } catch (error) {
        console.error("Dashboard load failed:", error);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const stats = [
    { label: "Fleet Size", value: loading ? "..." : fleetCount?.toString() || "0", change: 1 },
    { label: "Active Trips", value: loading ? "..." : activeTrips?.toString() || "0", change: 2 },
    { label: "Avg Risk", value: "0.44", change: -3 },
  ];

  return (
    <div ref={containerRef}>
      <DashboardPageTemplate
        title="Fleet Dashboard"
        subtitle="Real-time monitoring of routes, drivers, and fleet health"
        stats={stats}
      >
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          {/* Vehicle Status Chart */}
          <Card className="glass rounded-xl animate-card">
            <CardHeader>
              <CardTitle className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Fleet Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-[220px] w-full" />
              ) : (
                <VehicleStatusChart
                  active={vehicleStatuses.active}
                  inactive={vehicleStatuses.inactive}
                  inMaintenance={vehicleStatuses.inMaintenance}
                />
              )}
            </CardContent>
          </Card>

          {/* Trip Status Chart */}
          <Card className="glass rounded-xl animate-card">
            <CardHeader>
              <CardTitle className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                Trip Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <Skeleton className="h-[220px] w-full" />
              ) : (
                <TripStatusChart statuses={tripStatuses} />
              )}
            </CardContent>
          </Card>
        </div>

        {/* System Status */}
        <Card className="glass rounded-xl mt-4 animate-card">
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-4">
              Currently monitoring {fleetCount} vehicles across Singapore operations.
            </p>
            {loading ? (
              <Skeleton className="h-16 w-full" />
            ) : (
              <div className="rounded-lg bg-black/20 p-4 border border-white/5">
                <h4 className="text-sm font-bold text-[#70d2ff] mb-1">Nominal</h4>
                <p className="text-sm text-[#bdc8d0]">
                  Connected to TraceData Backend (v0.1.0). Seeded data for &quot;Singapore Logistics Hub&quot; and &quot;Tuas Haulage Solutions&quot; is active.
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </DashboardPageTemplate>
    </div>
  );
}
