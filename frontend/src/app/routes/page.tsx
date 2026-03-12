"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { MapIcon, NavigationIcon, RulerIcon } from "lucide-react";

type Route = {
  id: string;
  name: string;
  startPoint: string;
  endPoint: string;
  distance: string;
  status: "active" | "planned" | "inactive";
};

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
      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-tighter">
        {row.getValue("startPoint")}
      </span>
    ),
  },
  {
    accessorKey: "endPoint",
    header: "B",
    cell: ({ row }) => (
      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-tighter">
        {row.getValue("endPoint")}
      </span>
    ),
  },
  {
    accessorKey: "distance",
    header: "Dist",
    cell: ({ row }) => (
      <div className="flex items-center gap-1 text-slate-400">
        <RulerIcon className="w-3 h-3" />
        <span className="text-[11px] font-mono">
          {row.getValue("distance")}
        </span>
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
            "capitalize font-semibold text-[10px] px-2 py-0",
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
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Network</h2>
        <p className="text-slate-500 font-medium">
          Logistics topology and path optimization metrics.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <MapIcon className="w-4 h-4" />
              Total Vectors
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">
              {data.length}
            </div>
          </CardContent>
        </Card>

        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <NavigationIcon className="w-4 h-4" />
              Operational
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">
              {data.filter((r) => r.status === "active").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="border rounded-lg p-1 bg-white">
        <DataTable columns={columns} data={data} filterKey="name" />
      </div>
    </div>
  );
}
