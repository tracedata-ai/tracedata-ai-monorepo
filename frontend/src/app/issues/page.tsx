"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  ShieldAlertIcon,
} from "lucide-react";

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
    cell: ({ row }) => (
      <span className="font-mono text-[11px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
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
            "capitalize font-semibold text-[10px] px-2 py-0",
            severity === "low" && "bg-slate-100 text-slate-600",
            severity === "medium" && "bg-yellow-100 text-yellow-700",
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
            "capitalize font-semibold text-[10px]",
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

const data: Issue[] = [
  {
    id: "ISS-001",
    type: "safety",
    description: "Harsh braking detected - Route 5",
    severity: "high",
    status: "open",
  },
  {
    id: "ISS-002",
    type: "maintenance",
    description: "Low tire pressure - Vehicle V-902",
    severity: "medium",
    status: "open",
  },
  {
    id: "ISS-003",
    type: "delay",
    description: "Traffic congestion on East Coast Pkwy",
    severity: "low",
    status: "resolved",
  },
  {
    id: "ISS-004",
    type: "safety",
    description: "Potential collision near-miss",
    severity: "critical",
    status: "open",
  },
];

export default function IssuesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Incident Logs</h2>
        <p className="text-slate-500">
          Critical monitoring of fleet anomalies and driver safety events.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border shadow-none border-t-2 border-red-500">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <ShieldAlertIcon className="w-4 h-4 text-red-500" />
              Active Alerts
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-red-500 leading-none">
              {data.filter((i) => i.status === "open").length}
            </div>
          </CardContent>
        </Card>

        <Card className="border shadow-none border-t-2 border-slate-200">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <CheckCircle2Icon className="w-4 h-4 text-slate-400" />
              Resolved Today
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-500 leading-none">
              {data.filter((i) => i.status === "resolved").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="border rounded-lg p-1 bg-white">
        <DataTable columns={columns} data={data} filterKey="description" />
      </div>
    </div>
  );
}
