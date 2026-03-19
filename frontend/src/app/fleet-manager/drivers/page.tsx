"use client";

import { useEffect, useState } from "react";
import { getDrivers } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { type DriverRow } from "@/lib/sample-data";
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

export default function DriversPage() {
  const [drivers, setDrivers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDrivers() {
      try {
        const data = await getDrivers();
        // Map backend Driver to frontend DriverRow
        const mapped = data.map((d) => ({
          id: d.id,
          name: `${d.first_name} ${d.last_name}`,
          assignedRoute: "Active Route", // Mock/Placeholder for now
          hoursToday: Math.random() * 8, // Placeholder
          fatigueRisk: d.experience_level === "novice" ? "High" : "Low",
        }));
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
            <DataTable columns={columns} data={drivers} />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
