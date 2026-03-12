"use client";

import { useState } from "react";
import { dashboardConfig, VehicleProfile } from "@/config/dashboard";
import { Truck, MapPin, Activity, SignalHigh, Navigation, BatteryCharging, Wrench, PowerOff } from "lucide-react";
import Link from "next/link";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { fleetColumns } from "./fleet-columns";

function VehicleDetailContent({ vehicle }: { vehicle: VehicleProfile }) {
  const statusCls =
    vehicle.status === 'In Transit' ? 'bg-brand-teal/10 text-brand-teal border-brand-teal/20' :
    vehicle.status === 'Charging' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
    vehicle.status === 'Maintenance' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
    'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
  const statusIcon =
    vehicle.status === 'In Transit' ? <Navigation className="w-3 h-3" /> :
    vehicle.status === 'Charging' ? <BatteryCharging className="w-3 h-3" /> :
    vehicle.status === 'Maintenance' ? <Wrench className="w-3 h-3" /> :
    <PowerOff className="w-3 h-3" />
  const signalCls = vehicle.signal === 'Strong' ? 'text-brand-teal' : vehicle.signal === 'Medium' ? 'text-amber-500' : 'text-red-500'

  return (
    <>
      <div className="px-6 pb-4 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-foreground text-lg leading-tight font-mono">{vehicle.id}</h4>
            <p className="text-xs font-bold text-muted-foreground mt-1 tracking-widest uppercase">{vehicle.plateNumber}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className={`p-3 rounded-lg border flex items-center gap-2 font-bold text-sm ${statusCls}`}>
            {statusIcon} {vehicle.status}
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-border flex flex-col justify-center">
            <p className="text-xs text-slate-500 uppercase font-bold mb-0.5 tracking-wider">Signal</p>
            <div className="flex items-center gap-1.5">
              <SignalHigh className={`w-3.5 h-3.5 ${signalCls}`} />
              <span className="text-xs font-bold text-foreground">{vehicle.signal}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-brand-blue" /> Diagnostics & Stats
          </h5>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Model</p>
              <p className="text-sm font-bold text-foreground mt-1 truncate">{vehicle.model}</p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Total Op Hours</p>
              <p className="text-sm font-bold text-foreground font-mono mt-1">{vehicle.operatingHours.toLocaleString()}h</p>
            </div>
          </div>
        </div>

        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <MapPin className="w-4 h-4 text-brand-teal" /> Context
          </h5>
          <div className="space-y-3">
            <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-border flex justify-between items-center">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Driver</p>
              {vehicle.driver ? (
                <Link href={`/dashboard/drivers/${vehicle.driver}`} className="text-sm font-bold text-brand-blue hover:underline">
                  {vehicle.driver}
                </Link>
              ) : (
                <p className="text-sm font-medium text-muted-foreground">Unassigned</p>
              )}
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-border">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Last Loc</p>
              <p className="text-sm font-bold text-foreground">{vehicle.location || 'Unknown'}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

export default function FleetPage() {
  const { vehicles } = dashboardConfig;
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="fleet-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">Fleet Telemetry</h2>
            <p className="text-muted-foreground mt-1 text-sm">Real-time vehicle tracking and status monitoring.</p>
          </div>
          <div className="flex gap-3">
            <button className="bg-background border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:bg-muted transition-colors shadow-sm">Export Data</button>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">Register Vehicle</button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <DataTable
          columns={fleetColumns}
          data={vehicles}
          selectedId={selectedVehicleId}
          onRowClick={(vehicle) => setSelectedVehicleId(vehicle.id)}
        />
      </div>

      <DetailSheet
        isOpen={!!selectedVehicleId}
        onClose={() => setSelectedVehicleId(null)}
        title="Vehicle Details"
        deepLink={selectedVehicle ? `/dashboard/fleet/${selectedVehicle.id}` : undefined}
      >
        {selectedVehicle && <VehicleDetailContent vehicle={selectedVehicle} />}
      </DetailSheet>
    </div>
  );
}
