/**
 * Expeditions (Trips) Management Page
 * 
 * Monitors the lifecycle of vehicle paths, including real-time telemetry
 * streams and operational status (ongoing, completed, delayed).
 */

"use client";

import { DataTable } from "@/components/shared/DataTable";
import { StatCard } from "@/components/shared/StatCard";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { TruckIcon, TimerIcon, CheckCircle2Icon } from "lucide-react";

/**
 * Trip Record Object
 * Tracks the movement of a vehicle and driver through a scheduled route.
 */
type Trip = {
  id: string; // T-1001 format
  vehicleId: string;
  driverName: string;
  startTime: string;
  status: "ongoing" | "completed" | "delayed"; // Real-time transit status
};

/**
 * Column Definitions
 */
const columns: ColumnDef<Trip>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
    cell: ({ row }) => (
      <span className="font-mono text-xs font-bold text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded border border-slate-200">
        {row.getValue("id")}
      </span>
    ),
  },
  {
    accessorKey: "vehicleId",
    header: "Vehicle",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <TruckIcon className="w-4 h-4 text-slate-400" />
        <span className="font-medium text-slate-700">
          {row.getValue("vehicleId")}
        </span>
      </div>
    ),
  },
  {
    accessorKey: "driverName",
    header: "Driver",
    cell: ({ row }) => (
      <span className="font-semibold text-slate-800">
        {row.getValue("driverName")}
      </span>
    ),
  },
  {
    accessorKey: "startTime",
    header: "Departure",
    cell: ({ row }) => (
      <span className="text-slate-500 font-medium">
        {row.getValue("startTime")}
      </span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge
          variant={status === "ongoing" ? "default" : "outline"}
          className={cn(
            "capitalize font-semibold text-xs px-2 py-0",
            status === "ongoing" && "bg-slate-700 text-white",
            status === "completed" && "border-slate-300 text-slate-400",
            status === "delayed" && "border-orange-200 text-orange-600 bg-orange-50",
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

import { useEffect, useState } from "react";
import { entitiesApi, BackendTrip } from "@/lib/api";

export default function TripsPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadTrips() {
      try {
        setLoading(true);
        const response = await entitiesApi.getTrips();
        const mapped: Trip[] = response.items.map((item: BackendTrip) => {
          // Map backend status to frontend literal types
          let status: Trip["status"] = "ongoing";
          if (item.status === "completed") status = "completed";
          else if (item.status === "cancelled") status = "delayed"; // Mapping cancelled to delayed for now as catch-all
          
          return {
            id: `T-${item.id.slice(0, 4).toUpperCase()}`,
            vehicleId: item.vehicle_id.slice(0, 8),
            driverName: "Professional Driver",
            startTime: new Date(item.start_time).toLocaleString(),
            status,
          };
        });
        setTrips(mapped);
      } catch (err) {
        console.error("Failed to load trips:", err);
      } finally {
        setLoading(false);
      }
    }
    loadTrips();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500 animate-pulse">Synchronizing with TraceData network...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Transit Tracking</h2>
        <p className="text-slate-500 font-medium">
          Real-time monitoring of active expeditions and completed paths.
        </p>
      </div>

      {/* Overview Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Active Now"
          value={trips.filter((t) => t.status === "ongoing").length}
          icon={TimerIcon}
          iconClassName="text-slate-500"
        />

        <StatCard
          title="Completed"
          value={trips.filter((t) => t.status === "completed").length}
          icon={CheckCircle2Icon}
          iconClassName="text-slate-500"
        />
      </div>

      {/* Main Data Table */}
      <div className="">
        <DataTable columns={columns} data={trips} filterKey="id" />
      </div>
    </div>
  );
}
