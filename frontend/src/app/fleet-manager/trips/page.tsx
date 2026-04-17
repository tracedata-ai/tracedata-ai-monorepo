"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getTrips, type Trip } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const statusClass: Record<string, string> = {
  active: "bg-blue-500",
  completed: "bg-green-600",
  zombie: "bg-gray-500",
};

const columns: ColumnDef<Trip>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
    cell: (info) => (
      <span className="font-mono text-xs">{(info.getValue() as string).slice(0, 16)}…</span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: (info) => {
      const s = info.getValue() as string;
      return (
        <Badge className={`${statusClass[s] ?? "bg-gray-500"} text-white capitalize`}>{s}</Badge>
      );
    },
  },
  {
    accessorKey: "driver_id",
    header: "Driver ID",
    cell: (info) => (
      <span className="font-mono text-xs">{(info.getValue() as string).slice(0, 12)}…</span>
    ),
  },
  {
    accessorKey: "safety_score",
    header: "Trip Score (/100)",
    cell: (info) => {
      const raw = info.getValue();
      if (raw == null) return <span className="text-muted-foreground text-sm">Pending</span>;
      const v = Number(raw);
      if (isNaN(v)) return <span className="text-muted-foreground text-sm">Pending</span>;
      const color = v >= 80 ? "text-green-600" : v >= 55 ? "text-yellow-600" : "text-red-600";
      return (
        <span className={`font-semibold ${color}`}>
          {v.toFixed(1)}<span className="font-normal text-muted-foreground text-xs"> / 100</span>
        </span>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: "Started",
    cell: (info) => {
      const v = info.getValue() as string;
      return v ? new Date(v).toLocaleString() : "—";
    },
  },
];

export default function TripsPage() {
  const router = useRouter();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTrips()
      .then(setTrips)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const active = trips.filter((t) => t.status === "active").length;
  const completed = trips.filter((t) => t.status === "completed").length;
  const scored = trips.filter((t) => (t as Trip & { safety_score?: number }).safety_score != null).length;

  const stats = [
    { label: "Active", value: loading ? "..." : active.toString() },
    { label: "Completed", value: loading ? "..." : completed.toString() },
    { label: "Scored", value: loading ? "..." : scored.toString() },
  ];

  return (
    <DashboardPageTemplate
      title="Trips"
      subtitle="Click a row to view full trip analysis — scoring, safety events, coaching & sentiment"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Trip Log</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <DataTable
              columns={columns}
              data={trips}
              searchPlaceholder="Search trips…"
              onRowClick={(row) => router.push(`/fleet-manager/trips/${row.id}`)}
            />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
