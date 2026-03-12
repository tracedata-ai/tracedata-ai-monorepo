"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  Truck,
  MapPin,
  Activity,
  Navigation,
  BatteryCharging,
  Wrench,
  PowerOff,
  SignalHigh
} from "lucide-react";
import { InfoCard } from "@/components/shared/InfoCard";
import { MetricCard } from "@/components/shared/MetricCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function VehicleDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const vehicleId = resolvedParams.id;
  
  const vehicle = dashboardConfig.vehicles.find((v) => v.id === vehicleId);
  
  if (!vehicle) {
    notFound();
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Transit': return 'text-brand-teal';
      case 'Charging': return 'text-blue-500';
      case 'Maintenance': return 'text-amber-500';
      default: return 'text-slate-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'In Transit': return Navigation;
      case 'Charging': return BatteryCharging;
      case 'Maintenance': return Wrench;
      default: return PowerOff;
    }
  };

  return (
    <DashboardPageTemplate
      title={vehicle.id}
      description={`Asset Management Profile • ${vehicle.plateNumber}`}
      breadcrumbs={
        <>
          <Link href="/dashboard/fleet" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-3 h-3" />
            Fleet Telemetry
          </Link>
          <ChevronRight className="w-3 h-3 mx-2 opacity-30" />
          <span className="text-slate-900">{vehicle.id}</span>
        </>
      }
      headerActions={
        <>
          <Button variant="outline" size="sm">Maintenance Log</Button>
          <Button size="sm">Command Center</Button>
        </>
      }
    >
      <DetailContentTemplate
        heroIcon={Truck}
        heroTitle={vehicle.id}
        heroSubtitle={vehicle.plateNumber}
        highlights={[
          {
            label: "Live Status",
            value: vehicle.status,
            icon: getStatusIcon(vehicle.status),
            className: getStatusColor(vehicle.status)
          },
          {
            label: "Connectivity",
            value: vehicle.signal || 'Unknown',
            icon: SignalHigh,
            iconColor: vehicle.signal === 'Strong' ? 'text-brand-teal' : 'text-amber-500'
          }
        ]}
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <InfoCard
              title="Asset Diagnostics"
              icon={Activity}
              items={[
                { label: "Model / Asset Type", value: vehicle.model },
                { label: "Operating Hours", value: `${vehicle.operatingHours.toLocaleString()} hrs`, className: "font-mono" }
              ]}
            >
               <div className="mt-8 pt-8 border-t border-slate-100 flex justify-between items-center">
                  <div>
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Telemetry Signal Status</p>
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-black text-slate-900">{vehicle.signal}</span>
                      <div className="flex gap-1">
                        {[1, 2, 3].map(i => (
                          <div key={i} className={cn(
                            "w-1.5 h-5 rounded-full",
                            i === 1 && "bg-brand-teal",
                            i === 2 && (vehicle.signal === 'Strong' || vehicle.signal === 'Medium' ? "bg-brand-teal" : "bg-slate-200"),
                            i === 3 && (vehicle.signal === 'Strong' ? "bg-brand-teal" : "bg-slate-200")
                          )} />
                        ))}
                      </div>
                    </div>
                  </div>
                  <SignalHigh className={cn(
                    "w-10 h-10",
                    vehicle.signal === 'Strong' ? 'text-brand-teal' : 'text-amber-500'
                  )} />
               </div>
            </InfoCard>

            <InfoCard
              title="Current Context"
              icon={MapPin}
              items={[
                { 
                  label: "Assigned Driver", 
                  value: vehicle.driver ? (
                    <Link href={`/dashboard/drivers/${vehicle.driver}`} className="text-brand-blue font-bold hover:underline">
                       {vehicle.driver}
                    </Link>
                  ) : "Unassigned"
                },
                { 
                  label: "Last Known Location", 
                  value: vehicle.location || 'Location unavailable',
                  icon: Navigation,
                  className: "col-span-2"
                }
              ]}
            />
          </div>

          <div className="space-y-8">
            <MetricCard
              label="Health Score"
              value="98"
              icon={Activity}
              iconColor="text-brand-teal"
              className="bg-brand-teal/[0.02] border-brand-teal/10"
            >
              <p className="text-xs text-slate-400 font-medium leading-relaxed mt-4">Asset is performing within optimal parameters according to real-time diagnostics.</p>
            </MetricCard>

            <InfoCard
              title="Maintenance Status"
              icon={Wrench}
            >
               <div className="flex flex-col items-center justify-center py-6 text-center opacity-40">
                  <div className="w-12 h-12 rounded-full border border-dashed border-slate-300 flex items-center justify-center mb-4">
                    <Truck className="w-5 h-5 text-slate-400" />
                  </div>
                  <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">No service needed</p>
               </div>
            </InfoCard>
          </div>
        </div>
      </DetailContentTemplate>
    </DashboardPageTemplate>
  );
}
