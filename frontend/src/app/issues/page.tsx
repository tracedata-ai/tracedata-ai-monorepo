/**
 * Incident Logs (Issues) Page
 *
 * Central monitoring point for fleet anomalies, safety events, and
 * maintenance alerts. Tracks issue severity and resolution status.
 */

"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { StatCard } from "@/components/shared/StatCard";
import {
  CheckCircle2Icon,
  ShieldAlertIcon,
} from "lucide-react";

/**
 * Issue Context Object
 */
type Issue = {
  id: string; // ISS-001 format
  type: "maintenance" | "safety" | "delay";
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "resolved";
};

/**
 * Column Definitions
 */
const columns: ColumnDef<Issue>[] = [
  {
    accessorKey: "id",
    header: "Issue ID",
    cell: ({ row }) => (
      <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
        {row.getValue("id")}
      </span>
    ),
  },
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-slate-400" />
        <span className="capitalize font-semibold text-slate-700">
          {row.getValue("type")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => (
      <span className="text-slate-600 font-medium">
        {row.getValue("description")}
      </span>
    ),
  },
  {
    accessorKey: "severity",
    header: "Severity",
    cell: ({ row }) => {
      const severity = row.getValue("severity") as string;
      return (
        <Badge
          className={cn(
            "capitalize font-semibold text-xs px-2 py-0",
            severity === "low" && "bg-slate-100 text-slate-600",
            severity === "medium" && "bg-blue-50 text-blue-700",
            severity === "high" && "bg-orange-100 text-orange-700",
            severity === "critical" && "bg-red-600 text-white",
          )}
        >
          {severity}
        </Badge>
      );
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge
          variant={status === "resolved" ? "outline" : "default"}
          className={cn(
            "capitalize font-semibold text-xs",
            status === "resolved"
              ? "border-slate-200 text-slate-500"
              : "bg-slate-800 text-white",
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

import { useEffect, useState } from "react";
import { entitiesApi, BackendIssue } from "@/lib/api";

export default function IssuesPage() {
  const [issues, setIssues] = useState<Issue[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadIssues() {
      try {
        setLoading(true);
        const data = await entitiesApi.getIssues();
        const mapped: Issue[] = data.items.map((item: BackendIssue) => {
          // Safe type mapping for severity
          let severity: Issue["severity"] = "low";
          if (["low", "medium", "high", "critical"].includes(item.severity)) {
            severity = item.severity as Issue["severity"];
          }

          // Safe type mapping for status
          let status: Issue["status"] = "open";
          if (["open", "resolved"].includes(item.status)) {
            status = item.status as Issue["status"];
          }

          // Safe type mapping for issue type
          let type: Issue["type"] = "maintenance";
          const lowerType = item.issue_type.toLowerCase();
          if (["maintenance", "safety", "delay"].includes(lowerType)) {
            type = lowerType as Issue["type"];
          }

          return {
            id: `ISS-${item.id.slice(0, 4).toUpperCase()}`,
            type,
            description: item.description,
            severity,
            status,
          };
        });
        setIssues(mapped);
      } catch (err) {
        console.error("Failed to load issues:", err);
        setError("Could not connect to the TraceData network.");
      } finally {
        setLoading(false);
      }
    }
    loadIssues();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500 animate-pulse">Synchronizing with TraceData network...</div>;
  }

  if (error) {
    return (
      <div className="p-8 text-center text-red-500">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Incident Logs</h2>
        <p className="text-slate-500 font-medium">
          Critical monitoring of fleet anomalies and driver safety events.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Active Alerts"
          value={issues.filter((i) => i.status === "open").length}
          icon={ShieldAlertIcon}
          className="border-t-2 border-red-500"
          valueClassName="text-red-500"
          iconClassName="text-red-500"
        />

        <StatCard
          title="Resolved"
          value={issues.filter((i) => i.status === "resolved").length}
          icon={CheckCircle2Icon}
        />
      </div>

      {/* Main Data Table */}
      <div className="">
        <DataTable columns={columns} data={issues} filterKey="description" />
      </div>
    </div>
  );
}
