"use client";

import { useState } from "react";
import { dashboardConfig, VehicleProfile } from "@/config/dashboard";
import { Truck, MapPin, Activity, SignalHigh, Navigation, BatteryCharging, Wrench, PowerOff, ShieldAlert, User, Search } from "lucide-react";
import Link from "next/link";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { fleetColumns } from "./fleet-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

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
    <DetailContentTemplate
      heroIcon={Truck}
      heroTitle={vehicle.id}
      heroSubtitle={vehicle.plateNumber}
      highlights={[
        {
          label: "Live Status",
          value: vehicle.status,
          icon: statusIcon,
          className: statusCls
        },
        {
          label: "Connectivity",
          value: vehicle.signal || 'Unknown',
          icon: SignalHigh,
          iconColor: vehicle.signal === 'Strong' ? 'text-brand-teal' : vehicle.signal === 'Medium' ? 'text-amber-500' : 'text-red-500'
        }
      ]}
    >
      <div className="space-y-6">
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
    </DetailContentTemplate>
  );
}

export default function FleetPage() {
  const { vehicles } = dashboardConfig;
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const selectedVehicle = vehicles.find(v => v.id === selectedVehicleId) || null;

  return (
    <DashboardPageTemplate
      title="Fleet Telemetry"
      description="Real-time vehicle tracking and status monitoring."
      headerActions={
        <>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" placeholder="Search vehicles..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
          </div>
          <Button>Register Vehicle</Button>
        </>
      }
      stats={
        <>
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
        </>
      }
    >
      <DataTable
        columns={fleetColumns}
        data={vehicles}
        selectedId={selectedVehicleId}
        onRowClick={(vehicle) => setSelectedVehicleId(vehicle.id)}
      />

      <DetailSheet
        isOpen={!!selectedVehicleId}
        onClose={() => setSelectedVehicleId(null)}
        title="Vehicle Details"
        deepLink={selectedVehicle ? `/dashboard/fleet/${selectedVehicle.id}` : undefined}
      >
        {selectedVehicle && <VehicleDetailContent vehicle={selectedVehicle} />}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}
