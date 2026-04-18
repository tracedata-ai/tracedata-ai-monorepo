"use client";

import { useEffect, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import { getDrivers, getTrips, getRoutes, type Driver, type Trip, type Route } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertTriangle, Activity, BookOpen } from "lucide-react";
import { coachingQueue, type CoachingEntry } from "@/lib/sample-data";

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

const CATEGORY_META: Record<string, { label: string; icon: ReactNode }> = {
  fatigue_management: { label: "Fatigue Mgmt",   icon: <AlertTriangle className="h-3 w-3" /> },
  harsh_braking:      { label: "Harsh Braking",  icon: <Activity      className="h-3 w-3" /> },
  overspeed:          { label: "Overspeed",       icon: <AlertTriangle className="h-3 w-3" /> },
  route_deviation:    { label: "Route Deviation", icon: <Activity      className="h-3 w-3" /> },
  idle_time:          { label: "Idle Time",       icon: <BookOpen      className="h-3 w-3" /> },
  fuel_efficiency:    { label: "Fuel Efficiency", icon: <BookOpen      className="h-3 w-3" /> },
};

const PRIORITY_BADGE: Record<CoachingEntry["priority"], string> = {
  high:   "bg-[var(--error)] text-white",
  medium: "bg-[var(--warning)] text-white",
  low:    "bg-blue-500 text-white",
};

type CoachingFilter = "All" | "High" | "Medium";

function CoachingPriorityQueue() {
  const [filter, setFilter] = useState<CoachingFilter>("All");
  const filtered = coachingQueue.filter(c =>
    filter === "All" ? true : c.priority === filter.toLowerCase()
  );
  return (
    <Card className="glass rounded-xl animate-in fade-in slide-in-from-bottom-4 duration-500 fill-mode-both">
      <CardHeader>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-4 w-4 text-[#6366f1]" />
            Coaching Priority Queue
          </CardTitle>
          <div className="flex items-center gap-1">
            {(["All", "High", "Medium"] as CoachingFilter[]).map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`rounded-md px-3 py-1 text-xs font-semibold transition-colors ${
                  filter === f
                    ? "bg-[#6366f1] text-white"
                    : "bg-[#f3f4f6] text-[#6b7280] hover:bg-[#e5e7eb] hover:text-[#111827]"
                }`}>{f}</button>
            ))}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {filtered.length === 0
          ? <p className="py-6 text-center text-sm text-[#9ca3af]">No items for this filter.</p>
          : <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
              {filtered.map((c, i) => {
                const meta = CATEGORY_META[c.category] ?? { label: c.category, icon: <BookOpen className="h-3 w-3" /> };
                return (
                  <div key={`${c.driverId}-${i}`}
                    className="animate-in fade-in slide-in-from-bottom-2 fill-mode-both rounded-lg border border-[#e5e7eb] bg-white p-3 shadow-sm space-y-2"
                    style={{ animationDelay: `${i * 60}ms` }}>
                    <p className="truncate text-xs font-semibold text-[#111827]">{c.driverName}</p>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="flex items-center gap-1 rounded bg-[#f3f4f6] px-1.5 py-0.5 text-[10px] font-medium text-[#374151]">
                        {meta.icon}{meta.label}
                      </span>
                      <span className={`rounded px-1.5 py-0.5 text-[9px] font-bold uppercase ${PRIORITY_BADGE[c.priority]}`}>
                        {c.priority}
                      </span>
                    </div>
                    <p className="text-[11px] leading-relaxed text-[#6b7280]">{c.message}</p>
                    <p className="text-[10px] text-[#9ca3af]">
                      {new Date(c.created_at).toLocaleDateString("en-SG", { day: "numeric", month: "short", year: "numeric" })}
                    </p>
                  </div>
                );
              })}
            </div>
        }
      </CardContent>
    </Card>
  );
}

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
      <CoachingPriorityQueue />
    </DashboardPageTemplate>
  );
}
