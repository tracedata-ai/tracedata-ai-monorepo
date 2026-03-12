"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { TruckIcon, TimerIcon, MapPinIcon } from "lucide-react";

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
    cell: ({ row }) => <span className="font-mono text-[11px] font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">{row.getValue("id")}</span>,
  },
  {
    accessorKey: "vehicleId",
    header: "Vehicle ID",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <TruckIcon className="w-4 h-4 text-slate-400" />
        <span className="font-medium text-slate-700">{row.getValue("vehicleId")}</span>
      </div>
    ),
  },
  {
    accessorKey: "driverName",
    header: "Driver",
    cell: ({ row }) => <span className="text-slate-600 font-medium">{row.getValue("driverName")}</span>,
  },
  {
    accessorKey: "startTime",
    header: "Start Time",
    cell: ({ row }) => (
      <div className="flex items-center gap-2 text-slate-500">
        <TimerIcon className="w-3 h-3" />
        <span className="text-[11px] font-medium">{row.getValue("startTime")}</span>
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
          variant={status === "ongoing" ? "default" : status === "completed" ? "secondary" : "destructive"}
          className={cn(
            "capitalize font-semibold text-[10px] px-2 py-0",
            status === "ongoing" && "bg-slate-700 text-white",
            status === "completed" && "bg-slate-100 text-slate-700",
            status === "delayed" && "bg-red-500 text-white"
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
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900 text-balance">Expeditions</h2>
        <p className="text-slate-500">Real-time telemetry streams and trip lifecycle management.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <ActivityIcon className="w-4 h-4" />
              In Progress
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">
              {data.filter(t => t.status === "ongoing").length}
            </div>
          </CardContent>
        </Card>

        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <CheckCircle2Icon className="w-4 h-4" />
              Fulfilled
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">
              {data.filter(t => t.status === "completed").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="border rounded-lg p-1 bg-white">
        <DataTable columns={columns} data={data} filterKey="driverName" />
      </div>
    </div>
  );
}

import { ActivityIcon, CheckCircle2Icon } from "lucide-react";
