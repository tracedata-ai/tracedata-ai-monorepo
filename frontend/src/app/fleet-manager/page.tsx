"use client";

import { useEffect, useState } from "react";
import { getVehicles, getTrips } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";


export default function FleetManagerDashboard() {
  const [fleetCount, setFleetCount] = useState<number | null>(null);
  const [activeTrips, setActiveTrips] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [vehicles, trips] = await Promise.all([
          getVehicles(),
          getTrips(undefined, "active")
        ]);
        setFleetCount(vehicles.length);
        setActiveTrips(trips.length);
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
    <DashboardPageTemplate
      title="Fleet Dashboard"
      subtitle="Real-time monitoring of routes, drivers, and fleet health"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Fleet Overview</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground mb-4">
            Currently monitoring {fleetCount} vehicles across Singapore operations.
          </p>
          {loading ? (
             <Skeleton className="h-40 w-full" />
          ) : (
             <div className="rounded-lg bg-black/20 p-6 border border-white/5">
                <h4 className="text-lg font-bold text-[#70d2ff] mb-2">System Status: Nominal</h4>
                <p className="text-sm text-[#bdc8d0]">
                  Connected to TraceData Backend (v0.1.0). 
                  Seeded data for &quot;Singapore Logistics Hub&quot; and &quot;Tuas Haulage Solutions&quot; is active.
                </p>
             </div>
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
