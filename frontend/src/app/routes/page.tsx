/**
 * Logistics Network (Routes) Page
 *
 * Visualizes the logistics topology, including path optimization metrics,
 * distances, and route status (active, planned, inactive).
 */

"use client";

import { DataTable } from "@/components/shared/DataTable";
import { StatCard } from "@/components/shared/StatCard";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { NetworkIcon, NavigationIcon, RulerIcon, ZapIcon } from "lucide-react";

/**
 * Route Domain Object
 */
type Route = {
  id: string;
  name: string;
  startPoint: string;
  endPoint: string;
  distance: string;
  status: "active" | "planned" | "inactive";
};

/**
 * Column Definitions
 */
const columns: ColumnDef<Route>[] = [
  {
    accessorKey: "name",
    header: "Route Name",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <NavigationIcon className="w-4 h-4 text-slate-400 rotate-45" />
        <span className="font-semibold text-slate-800">
          {row.getValue("name")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "startPoint",
    header: "A",
    cell: ({ row }) => (
      <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">
        {row.getValue("startPoint")}
      </span>
    ),
  },
  {
    accessorKey: "endPoint",
    header: "B",
    cell: ({ row }) => (
      <span className="text-xs font-bold text-slate-500 uppercase tracking-tighter">
        {row.getValue("endPoint")}
      </span>
    ),
  },
  {
    accessorKey: "distance",
    header: "Distance",
    cell: ({ row }) => (
      <div className="flex items-center gap-1 text-slate-400">
        <RulerIcon className="w-3 h-3" />
        <span className="text-xs font-mono">{row.getValue("distance")}</span>
      </div>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge
          variant={status === "active" ? "default" : "outline"}
          className={cn(
            "capitalize font-semibold text-xs px-2 py-0",
            status === "active" && "bg-slate-700 text-white",
            status === "planned" &&
              "border-slate-300 text-slate-500 bg-slate-50",
            status === "inactive" && "border-red-200 text-red-500 bg-red-50",
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

/**
 * Mock Data
 */
const data: Route[] = [
  {
    id: "1",
    name: "North-South Express",
    startPoint: "Woodlands",
    endPoint: "HarbourFront",
    distance: "25km",
    status: "active",
  },
  {
    id: "2",
    name: "East Coast Loop",
    startPoint: "Changi",
    endPoint: "Marina Bay",
    distance: "18km",
    status: "active",
  },
  {
    id: "3",
    name: "Western Industrial",
    startPoint: "Tuas",
    endPoint: "Jurong East",
    distance: "12km",
    status: "planned",
  },
  {
    id: "4",
    name: "Central Orbit",
    startPoint: "Orchard",
    endPoint: "Ang Mo Kio",
    distance: "10km",
    status: "inactive",
  },
];

export default function RoutesPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Network</h2>
        <p className="text-slate-500 font-medium">
          Logistics topology and path optimization metrics.
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total Sectors"
          value={data.length}
          icon={NetworkIcon}
          iconClassName="text-slate-500"
        />

        <StatCard
          title="Active Paths"
          value={data.filter((r) => r.status === "active").length}
          icon={ZapIcon}
          iconClassName="text-slate-500"
        />
      </div>

      {/* Main Data Table */}
      <div className="">
        <DataTable columns={columns} data={data} filterKey="name" />
      </div>
    </div>
  );
}
