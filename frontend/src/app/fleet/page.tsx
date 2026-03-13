"use client";

import { useEffect, useState } from "react";
import { DataTable } from "@/components/shared/DataTable";
import { StatCard } from "@/components/shared/StatCard";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { TruckIcon, ActivityIcon } from "lucide-react";
import { cn } from "@/lib/utils";
import { entitiesApi, BackendVehicle } from "@/lib/api";

type Vehicle = {
  id: string;
  vin: string;
  plate: string;
  make: string;
  model: string;
  year: string;
  status: string;
};

const columns: ColumnDef<Vehicle>[] = [
  {
    accessorKey: "plate",
    header: "License Plate",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <TruckIcon className="w-4 h-4 text-slate-400" />
        <span className="font-bold text-slate-900">{row.getValue("plate")}</span>
      </div>
    ),
  },
  {
    accessorKey: "make",
    header: "Make/Model",
    cell: ({ row }) => (
      <div className="flex flex-col">
        <span className="text-sm font-semibold text-slate-700">{row.original.make}</span>
        <span className="text-xs text-slate-500">{row.original.model} ({row.original.year})</span>
      </div>
    ),
  },
  {
    accessorKey: "vin",
    header: "VIN",
    cell: ({ row }) => (
      <code className="text-[10px] font-mono bg-slate-100 px-1 py-0.5 rounded text-slate-500">
        {row.getValue("vin")}
      </code>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge
          className={cn(
            "capitalize font-semibold text-xs px-2 py-0",
            status === "active" && "bg-emerald-500 text-white",
            status === "maintenance" && "bg-orange-500 text-white",
            status === "retired" && "bg-slate-300 text-slate-600",
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

export default function FleetPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadFleet() {
      try {
        setLoading(true);
        const data = await entitiesApi.getFleet();
        const mapped: Vehicle[] = data.items.map((item: BackendVehicle) => ({
          id: item.id,
          vin: item.vin,
          plate: item.license_plate,
          make: item.make,
          model: item.model,
          year: item.year,
          status: item.status,
        }));
        setVehicles(mapped);
      } catch (err) {
        console.error("Failed to load fleet:", err);
        setError("Could not connect to the TraceData network.");
      } finally {
        setLoading(false);
      }
    }
    loadFleet();
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-slate-500 animate-pulse">Synchronizing with TraceData network...</div>;
  }

  if (error) {
    return (
      <div className="p-8 text-center">
        <div className="text-red-500 font-bold mb-2">Network Error</div>
        <div className="text-slate-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Fleet Inventory</h2>
        <p className="text-slate-500">Manage vehicle assets, maintenance cycles, and deployment status.</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total Vehicles"
          value={vehicles.length}
          icon={TruckIcon}
          iconClassName="text-slate-500"
        />
        <StatCard
          title="Active Assets"
          value={vehicles.filter(v => v.status === "active").length}
          icon={ActivityIcon}
          iconClassName="text-emerald-500"
        />
      </div>

      <div className="">
        <DataTable columns={columns} data={vehicles} filterKey="plate" />
      </div>
    </div>
  );
}
