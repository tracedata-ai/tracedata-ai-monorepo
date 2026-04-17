"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getSafetyEvents, type SafetyEvent } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const severityClass: Record<string, string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
};

const decisionClass: Record<string, string> = {
  escalate: "bg-red-600",
  monitor: "bg-yellow-600",
};

function SeverityBadge({ value }: { value: string }) {
  const cls = severityClass[value?.toLowerCase()] ?? "bg-gray-500";
  return <Badge className={`${cls} text-white capitalize`}>{value}</Badge>;
}

function DecisionBadge({ value }: { value: string | null }) {
  if (!value) return <span className="text-muted-foreground text-sm">—</span>;
  const cls = decisionClass[value?.toLowerCase()] ?? "bg-gray-500";
  return <Badge className={`${cls} text-white capitalize`}>{value}</Badge>;
}

const columns: ColumnDef<SafetyEvent>[] = [
  {
    accessorKey: "event_type",
    header: "Event Type",
    cell: (info) => (
      <span className="capitalize">{(info.getValue() as string).replace(/_/g, " ")}</span>
    ),
  },
  {
    accessorKey: "severity",
    header: "Severity",
    cell: (info) => <SeverityBadge value={info.getValue() as string} />,
  },
  {
    accessorKey: "decision",
    header: "Decision",
    cell: (info) => <DecisionBadge value={info.getValue() as string | null} />,
  },
  {
    accessorKey: "truck_id",
    header: "Truck",
    cell: (info) => (info.getValue() as string | null) ?? "—",
  },
  {
    accessorKey: "driver_id",
    header: "Driver",
    cell: (info) => (info.getValue() as string | null) ?? "—",
  },
  {
    accessorKey: "traffic_conditions",
    header: "Traffic",
    cell: (info) => (
      <span className="capitalize">{(info.getValue() as string | null) ?? "—"}</span>
    ),
  },
  {
    accessorKey: "event_timestamp",
    header: "Timestamp",
    cell: (info) => {
      const v = info.getValue() as string | null;
      return v ? new Date(v).toLocaleString() : "—";
    },
  },
];

export default function IssuesPage() {
  const router = useRouter();
  const [events, setEvents] = useState<SafetyEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSafetyEvents()
      .then(setEvents)
      .catch((err) => console.error("Failed to fetch safety events:", err))
      .finally(() => setLoading(false));
  }, []);

  const critical = events.filter((e) => e.severity?.toLowerCase() === "critical").length;
  const high = events.filter((e) => e.severity?.toLowerCase() === "high").length;
  const escalated = events.filter((e) => e.decision?.toLowerCase() === "escalate").length;

  const stats = [
    { label: "Total Events", value: loading ? "..." : events.length.toString(), change: 0 },
    { label: "Critical", value: loading ? "..." : critical.toString(), change: 0 },
    { label: "High", value: loading ? "..." : high.toString(), change: 0 },
    { label: "Escalated", value: loading ? "..." : escalated.toString(), change: 0 },
  ];

  return (
    <DashboardPageTemplate
      title="Safety Events"
      subtitle="Harsh events analysed by the Safety Agent — click a row for full details"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Harsh Events Log</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <DataTable
              columns={columns}
              data={events}
              searchPlaceholder="Search events…"
              onRowClick={(row) =>
                router.push(`/fleet-manager/issues/${row.event_id}`)
              }
            />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
