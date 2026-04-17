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
import { EventHeatMap } from "@/components/maps/EventHeatMap";
import { ChevronDown, ChevronRight } from "lucide-react";

// ── Badges ────────────────────────────────────────────────────────────────────

const severityClass: Record<string, string> = {
  critical: "bg-red-600",
  high:     "bg-orange-500",
  medium:   "bg-yellow-500",
  low:      "bg-blue-500",
};
const decisionClass: Record<string, string> = {
  escalate: "bg-red-600",
  monitor:  "bg-yellow-600",
};

function SeverityBadge({ value }: { value: string }) {
  return (
    <Badge className={`${severityClass[value?.toLowerCase()] ?? "bg-gray-500"} text-white capitalize`}>
      {value}
    </Badge>
  );
}
function DecisionBadge({ value }: { value: string | null }) {
  if (!value) return <span className="text-muted-foreground text-sm">—</span>;
  return (
    <Badge className={`${decisionClass[value?.toLowerCase()] ?? "bg-gray-500"} text-white capitalize`}>
      {value}
    </Badge>
  );
}

// ── Flat table columns ────────────────────────────────────────────────────────

const columns: ColumnDef<SafetyEvent>[] = [
  {
    accessorKey: "trip_id",
    header: "Trip",
    cell: (info) => (
      <span className="font-mono text-xs text-muted-foreground">
        {((info.getValue() as string) ?? "").slice(0, 8)}
      </span>
    ),
  },
  {
    accessorKey: "event_type",
    header: "Event",
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
    accessorKey: "driver_name",
    header: "Driver",
    cell: (info) => (info.getValue() as string | null) ?? "—",
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

// ── Grouped view ──────────────────────────────────────────────────────────────

type GroupBy = "none" | "trip" | "truck";

function GroupedEvents({
  events,
  groupBy,
  onRowClick,
}: {
  events: SafetyEvent[];
  groupBy: "trip" | "truck";
  onRowClick: (e: SafetyEvent) => void;
}) {
  const [collapsed, setCollapsed] = useState<Set<string>>(new Set());

  const groups = events.reduce<Record<string, SafetyEvent[]>>((acc, e) => {
    const key = (groupBy === "trip" ? e.trip_id : e.truck_id) ?? "Unknown";
    (acc[key] ??= []).push(e);
    return acc;
  }, {});

  const toggle = (key: string) =>
    setCollapsed((prev) => {
      const next = new Set(prev);
      next.has(key) ? next.delete(key) : next.add(key);
      return next;
    });

  const severityOrder = ["critical", "high", "medium", "low"];

  return (
    <div className="space-y-3">
      {Object.entries(groups)
        .sort(([, a], [, b]) => b.length - a.length)
        .map(([key, rows]) => {
          const isOpen = !collapsed.has(key);
          const counts = severityOrder.reduce<Record<string, number>>((acc, s) => {
            acc[s] = rows.filter((r) => r.severity?.toLowerCase() === s).length;
            return acc;
          }, {});
          const label = groupBy === "trip"
            ? `Trip ${key.slice(0, 8)}`
            : `Truck ${key}`;

          return (
            <div key={key} className="overflow-hidden rounded-xl border border-border bg-card">
              {/* Group header */}
              <button
                onClick={() => toggle(key)}
                className="flex w-full items-center gap-3 px-4 py-3 text-left hover:bg-muted/50 transition-colors"
              >
                {isOpen
                  ? <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
                  : <ChevronRight className="h-4 w-4 shrink-0 text-muted-foreground" />
                }
                <span className="font-mono text-sm font-semibold">{label}</span>
                {groupBy === "trip" && rows[0]?.truck_id && (
                  <span className="text-xs text-muted-foreground">{rows[0].truck_id}</span>
                )}
                <span className="text-xs text-muted-foreground">{rows.length} event{rows.length !== 1 ? "s" : ""}</span>
                <div className="ml-auto flex gap-1.5">
                  {severityOrder.map((s) =>
                    counts[s] > 0 ? (
                      <span
                        key={s}
                        className={`rounded px-1.5 py-0.5 text-[10px] font-bold text-white ${severityClass[s]}`}
                      >
                        {counts[s]} {s}
                      </span>
                    ) : null
                  )}
                </div>
              </button>

              {/* Rows */}
              {isOpen && (
                <div className="border-t border-border">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/40">
                      <tr>
                        {groupBy === "truck" && (
                          <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Trip</th>
                        )}
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Event</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Severity</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Decision</th>
                        <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {rows.map((e) => (
                        <tr
                          key={e.event_id}
                          onClick={() => onRowClick(e)}
                          className="cursor-pointer border-t border-border/50 hover:bg-muted/30 transition-colors"
                        >
                          {groupBy === "truck" && (
                            <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">
                              {e.trip_id.slice(0, 8)}
                            </td>
                          )}
                          <td className="px-4 py-2.5 capitalize">{e.event_type.replace(/_/g, " ")}</td>
                          <td className="px-4 py-2.5"><SeverityBadge value={e.severity} /></td>
                          <td className="px-4 py-2.5"><DecisionBadge value={e.decision} /></td>
                          <td className="px-4 py-2.5 text-xs text-muted-foreground">
                            {e.event_timestamp ? new Date(e.event_timestamp).toLocaleString() : "—"}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function IssuesPage() {
  const router  = useRouter();
  const [events, setEvents]   = useState<SafetyEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [groupBy, setGroupBy] = useState<GroupBy>("none");

  useEffect(() => {
    getSafetyEvents()
      .then(setEvents)
      .catch((err) => console.error("Failed to fetch safety events:", err))
      .finally(() => setLoading(false));
  }, []);

  const critical  = events.filter((e) => e.severity?.toLowerCase() === "critical").length;
  const high      = events.filter((e) => e.severity?.toLowerCase() === "high").length;
  const escalated = events.filter((e) => e.decision?.toLowerCase() === "escalate").length;

  const stats = [
    { label: "Total Events", value: loading ? "..." : events.length.toString(),  change: 0 },
    { label: "Critical",     value: loading ? "..." : critical.toString(),        change: 0 },
    { label: "High",         value: loading ? "..." : high.toString(),            change: 0 },
    { label: "Escalated",    value: loading ? "..." : escalated.toString(),       change: 0 },
  ];

  const handleRowClick = (row: SafetyEvent) =>
    router.push(`/fleet-manager/issues/${row.event_id}`);

  return (
    <DashboardPageTemplate
      title="Safety Events"
      subtitle="Harsh events analysed by the Safety Agent — click a row for full details"
      stats={stats}
    >
      <div className="flex flex-col gap-4">
        {/* Heatmap */}
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle>Safety Heatmap</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-105 w-full rounded-xl" />
            ) : (
              <EventHeatMap
                events={events
                  .filter((e) => e.lat != null && e.lon != null)
                  .map((e) => ({ lat: e.lat!, lon: e.lon!, severity: e.severity, event_type: e.event_type }))}
              />
            )}
          </CardContent>
        </Card>

        {/* Events table / grouped */}
        <Card className="glass rounded-xl">
          <CardHeader>
            <div className="flex items-center justify-between gap-3 flex-wrap">
              <CardTitle>Harsh Events Log</CardTitle>

              {/* Group-by control */}
              <div className="flex items-center rounded-lg border border-border bg-muted p-0.5 text-sm">
                {(["none", "trip", "truck"] as GroupBy[]).map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setGroupBy(opt)}
                    className={`rounded-md px-3 py-1 font-medium capitalize transition-colors ${
                      groupBy === opt
                        ? "bg-background text-foreground shadow-sm"
                        : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {opt === "none" ? "All" : `By ${opt}`}
                  </button>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, i) => (
                  <Skeleton key={i} className="h-10 w-full" />
                ))}
              </div>
            ) : groupBy === "none" ? (
              <DataTable
                columns={columns}
                data={events}
                searchPlaceholder="Search events…"
                onRowClick={handleRowClick}
              />
            ) : (
              <GroupedEvents
                events={events}
                groupBy={groupBy}
                onRowClick={handleRowClick}
              />
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardPageTemplate>
  );
}
