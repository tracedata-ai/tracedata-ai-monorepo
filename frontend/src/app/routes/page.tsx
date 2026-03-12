"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";

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
  },
  {
    accessorKey: "startPoint",
    header: "Start Point",
  },
  {
    accessorKey: "endPoint",
    header: "End Point",
  },
  {
    accessorKey: "distance",
    header: "Distance",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge 
          variant={status === "active" ? "default" : "secondary"}
          className={cn(
            "capitalize",
            status === "active" ? "bg-brand-teal hover:bg-brand-teal/80" : ""
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

const data: Route[] = [
  { id: "1", name: "North-South Express", startPoint: "Woodlands", endPoint: "HarbourFront", distance: "25km", status: "active" },
  { id: "2", name: "East Coast Loop", startPoint: "Changi", endPoint: "Marina Bay", distance: "18km", status: "active" },
  { id: "3", name: "Western Industrial", startPoint: "Tuas", endPoint: "Jurong East", distance: "12km", status: "planned" },
  { id: "4", name: "Central Orbit", startPoint: "Orchard", endPoint: "Ang Mo Kio", distance: "10km", status: "inactive" },
];

import { cn } from "@/lib/utils";

export default function RoutesPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Routes</h2>
        <p className="text-muted-foreground">Manage and monitor vehicle delivery routes.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Total Routes</h3>
          <p className="text-3xl font-bold text-brand-blue">{data.length}</p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Active Routes</h3>
          <p className="text-3xl font-bold text-brand-teal">
            {data.filter(r => r.status === "active").length}
          </p>
        </div>
      </div>

      <DataTable columns={columns} data={data} filterKey="name" />
    </div>
  );
}
