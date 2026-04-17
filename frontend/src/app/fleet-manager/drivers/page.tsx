"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getDrivers, getTrips, getRoutes, type Driver, type Trip, type Route } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

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

type DriverRow = {
  id: string;
  name: string;
  assignedRoute: string;
  hoursToday: number;
  fatigueRisk: "Low" | "Medium" | "High";
};

export default function DriversPage() {
  const router = useRouter();
  const [drivers, setDrivers] = useState<DriverRow[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDrivers() {
      try {
        const [driversData, tripsData, routesData] = await Promise.all([
          getDrivers(),
          getTrips(),
          getRoutes(),
        ]);
        const routeById = new Map(routesData.map((r: Route) => [r.id, r]));
        const activeTripByDriver = new Map(
          tripsData
            .filter((t: Trip) => t.status === "active")
            .map((t) => [t.driver_id, t])
        );

        const mapped: DriverRow[] = driversData.map((d: Driver) => {
          const activeTrip = activeTripByDriver.get(d.id);
          const routeName = activeTrip
            ? routeById.get(activeTrip.route_id)?.name ?? "Unassigned"
            : "Unassigned";
          const hoursToday = activeTrip
            ? Math.max(
                0,
                (Date.now() - new Date(activeTrip.created_at).getTime()) / 3_600_000
              )
            : 0;
          const fatigueRisk: DriverRow["fatigueRisk"] =
            hoursToday >= 8
              ? "High"
              : hoursToday >= 6 || d.experience_level === "novice"
                ? "Medium"
                : "Low";
          return {
          id: d.id,
          name: `${d.first_name} ${d.last_name}`,
          assignedRoute: routeName,
          hoursToday,
          fatigueRisk,
        };
        });
        setDrivers(mapped);
      } catch (error) {
        console.error("Failed to fetch drivers:", error);
      } finally {
        setLoading(false);
      }
    }
    loadDrivers();
  }, []);

  const stats = [
    { label: "Total Drivers", value: loading ? "..." : drivers.length, change: 1 },
    { label: "High Fatigue", value: loading ? "..." : drivers.filter(d => d.fatigueRisk === "High").length.toString(), change: -1 },
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
          {loading ? (
             <div className="space-y-4">
               <Skeleton className="h-10 w-full" />
               <Skeleton className="h-10 w-full" />
               <Skeleton className="h-10 w-full" />
             </div>
          ) : (
            <DataTable
              columns={columns}
              data={drivers}
              onRowClick={(row) => router.push(`/fleet-manager/drivers/${row.id}`)}
            />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
