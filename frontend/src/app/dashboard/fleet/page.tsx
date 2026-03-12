"use client";

import { useState } from "react";
import { dashboardConfig, VehicleProfile } from "@/config/dashboard";
import { Truck, MapPin, Activity, SignalHigh, Navigation, BatteryCharging, Wrench, PowerOff, ShieldAlert, Award } from "lucide-react";
import Link from "next/link";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { fleetColumns } from "./fleet-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";

function VehicleDetailContent({ vehicle }: { vehicle: VehicleProfile }) {
  const statusCls =
    vehicle.status === 'In Transit' ? 'text-brand-teal' :
    vehicle.status === 'Charging' ? 'text-blue-500' :
    vehicle.status === 'Maintenance' ? 'text-amber-500' :
    'text-slate-600'
  
  const statusIcon =
    vehicle.status === 'In Transit' ? Navigation :
    vehicle.status === 'Charging' ? BatteryCharging :
    vehicle.status === 'Maintenance' ? Wrench :
    PowerOff

  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-4 border-b border-border">
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
          <MetricCard
            compact
            label="Live Status"
            value={vehicle.status}
            icon={statusIcon}
            className={statusCls}
          />
          <MetricCard
            compact
            label="Connectivity"
            value={vehicle.signal || 'Unknown'}
            icon={SignalHigh}
            iconColor={vehicle.signal === 'Strong' ? 'text-brand-teal' : vehicle.signal === 'Medium' ? 'text-amber-500' : 'text-red-500'}
          />
        </div>
      </DashboardSection>

      <div className="p-6 space-y-6">
        <InfoCard
          title="Diagnostics & Stats"
          icon={Activity}
          items={[
            { label: "Model", value: vehicle.model },
            { label: "Total Op Hours", value: `${vehicle.operatingHours.toLocaleString()}h` }
          ]}
        />

        <InfoCard
          title="Operational Context"
          icon={MapPin}
          items={[
            { 
              label: "Assigned Driver", 
              value: vehicle.driver ? (
                <Link href={`/dashboard/drivers/${vehicle.driver}`} className="text-brand-blue hover:underline">
                  {vehicle.driver}
                </Link>
              ) : "Unassigned"
            },
            { label: "Last Known Location", value: vehicle.location || 'Unknown', className: "col-span-2" }
          ]}
        />
      </div>
    </div>
  );
}

export default function FleetPage() {
  const { vehicles } = dashboardConfig;
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="fleet-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border flex-shrink-0">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <h2 className="text-3xl font-black text-slate-900 tracking-tight">Fleet Telemetry</h2>
              <p className="text-muted-foreground mt-1 text-sm">Real-time vehicle tracking and status monitoring.</p>
            </div>
            <div className="flex gap-3">
              <button className="bg-background border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:bg-slate-50 transition-colors shadow-sm">Export Data</button>
              <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">Register Vehicle</button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
            <MetricCard
              label="Active Trucks"
              value={vehicles.filter(v => v.status === "In Transit").length}
              icon={Truck}
              iconColor="text-brand-blue"
            />
            <MetricCard
              label="Charging"
              value={vehicles.filter(v => v.status === "Charging").length}
              icon={BatteryCharging}
              iconColor="text-blue-500"
            />
            <MetricCard
              label="In Maintenance"
              value={vehicles.filter(v => v.status === "Maintenance").length}
              icon={Wrench}
              iconColor="text-amber-500"
            />
            <MetricCard
              label="Fleet Health"
              value="98.2%"
              icon={ShieldAlert}
              iconColor="text-emerald-500"
              trend={{ value: 0.5, label: "optimal", isPositive: true }}
            />
          </div>
        </DashboardSection>
      </header>

      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-8">
          <DataTable
            columns={fleetColumns}
            data={vehicles}
            selectedId={selectedVehicleId}
            onRowClick={(vehicle) => setSelectedVehicleId(vehicle.id)}
          />
        </DashboardSection>
      </main>

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
