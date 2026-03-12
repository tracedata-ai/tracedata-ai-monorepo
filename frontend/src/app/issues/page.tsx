"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Issue = {
  id: string;
  type: "maintenance" | "safety" | "delay";
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  status: "open" | "resolved";
};

const columns: ColumnDef<Issue>[] = [
  {
    accessorKey: "id",
    header: "Issue ID",
  },
  {
    accessorKey: "type",
    header: "Type",
    cell: ({ row }) => <span className="capitalize">{row.getValue("type")}</span>,
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "severity",
    header: "Severity",
    cell: ({ row }) => {
      const severity = row.getValue("severity") as string;
      return (
        <Badge 
          className={cn(
            "capitalize",
            severity === "low" && "bg-slate-500",
            severity === "medium" && "bg-yellow-500",
            severity === "high" && "bg-orange-500",
            severity === "critical" && "bg-red-600 animate-pulse"
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
        <Badge variant={status === "resolved" ? "outline" : "default"}>
          {status}
        </Badge>
      );
    },
  },
];

const data: Issue[] = [
  { id: "ISS-001", type: "safety", description: "Harsh braking detected - Route 5", severity: "high", status: "open" },
  { id: "ISS-002", type: "maintenance", description: "Low tire pressure - Vehicle V-902", severity: "medium", status: "open" },
  { id: "ISS-003", type: "delay", description: "Traffic congestion on East Coast Pkwy", severity: "low", status: "resolved" },
  { id: "ISS-004", type: "safety", description: "Potential collision near-miss", severity: "critical", status: "open" },
];

export default function IssuesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Issues</h2>
        <p className="text-muted-foreground">Track and resolve fleet and driver issues.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Open Issues</h3>
          <p className="text-3xl font-bold text-red-500">
            {data.filter(i => i.status === "open").length}
          </p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Resolved Today</h3>
          <p className="text-3xl font-bold text-brand-teal">
            {data.filter(i => i.status === "resolved").length}
          </p>
        </div>
      </div>

      <DataTable columns={columns} data={data} filterKey="description" />
    </div>
  );
}
