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

import { useEffect, useState } from "react";
import { entitiesApi, BackendRoute } from "@/lib/api";

export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadRoutes() {
      try {
        setLoading(true);
        const response = await entitiesApi.getRoutes();
        const mapped: Route[] = response.items.map((item: BackendRoute) => ({
          id: item.id,
          name: item.name,
          startPoint: item.start_location,
          endPoint: item.end_location,
          distance: `${item.estimated_distance}km`,
          status: "active", // Default since schema doesn't have status yet
        }));
        setRoutes(mapped);
      } catch (err) {
        console.error("Failed to load routes:", err);
        setError("Could not connect to the TraceData network.");
      } finally {
        setLoading(false);
      }
    }
    loadRoutes();
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
          value={routes.length}
          icon={NetworkIcon}
          iconClassName="text-slate-500"
        />

        <StatCard
          title="Active Paths"
          value={routes.filter((r) => r.status === "active").length}
          icon={ZapIcon}
          iconClassName="text-slate-500"
        />
      </div>

      {/* Main Data Table */}
      <div className="">
        <DataTable columns={columns} data={routes} filterKey="name" />
      </div>
    </div>
  );
}
