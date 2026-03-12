"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Trip = {
  id: string;
  vehicleId: string;
  driverName: string;
  startTime: string;
  status: "ongoing" | "completed" | "delayed";
};

const columns: ColumnDef<Trip>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
  },
  {
    accessorKey: "vehicleId",
    header: "Vehicle ID",
  },
  {
    accessorKey: "driverName",
    header: "Driver",
  },
  {
    accessorKey: "startTime",
    header: "Start Time",
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge 
          className={cn(
            "capitalize",
            status === "ongoing" && "bg-brand-blue hover:bg-brand-blue/80",
            status === "completed" && "bg-brand-teal hover:bg-brand-teal/80",
            status === "delayed" && "bg-red-500 hover:bg-red-500/80"
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

const data: Trip[] = [
  { id: "T-1001", vehicleId: "V-901", driverName: "Alex Chen", startTime: "2026-03-12 08:30", status: "ongoing" },
  { id: "T-1002", vehicleId: "V-902", driverName: "Sarah Lim", startTime: "2026-03-12 09:15", status: "ongoing" },
  { id: "T-1003", vehicleId: "V-903", driverName: "John Doe", startTime: "2026-03-11 14:00", status: "completed" },
  { id: "T-1004", vehicleId: "V-904", driverName: "Jane Smith", startTime: "2026-03-12 10:00", status: "delayed" },
];

export default function TripsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Trips</h2>
        <p className="text-muted-foreground">Real-time trip tracking and history.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Ongoing Trips</h3>
          <p className="text-3xl font-bold text-brand-blue">
            {data.filter(t => t.status === "ongoing").length}
          </p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Completed Today</h3>
          <p className="text-3xl font-bold text-brand-teal">
            {data.filter(t => t.status === "completed").length}
          </p>
        </div>
      </div>

      <DataTable columns={columns} data={data} filterKey="driverName" />
    </div>
  );
}
