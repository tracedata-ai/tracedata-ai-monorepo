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
import { DashboardSection } from "@/components/shared/DashboardSection";
import { MetricCard } from "@/components/shared/MetricCard";
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
      case 'In Transit': return 'bg-brand-teal/10 text-brand-teal border-brand-teal/20';
      case 'Charging': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'Maintenance': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'Idle': return 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700';
      default: return "";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'In Transit': return <Navigation className="w-5 h-5" />;
      case 'Charging': return <BatteryCharging className="w-5 h-5" />;
      case 'Maintenance': return <Wrench className="w-5 h-5" />;
      case 'Idle': return <PowerOff className="w-5 h-5" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden text-slate-900">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-100 flex-shrink-0">
        <DashboardSection gridCols={1} className="py-4">
          <nav className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest">
            <Link href="/dashboard/fleet" className="hover:text-brand-blue transition-colors flex items-center gap-1.5 -ml-2 px-2 py-1 rounded-full hover:bg-slate-50">
              <ArrowLeft className="w-3.5 h-3.5" />
              Fleet Telemetry
            </Link>
            <ChevronRight className="w-3.5 h-3.5 mx-3 opacity-30" />
            <span className="text-slate-900 dark:text-slate-100">{vehicle.id}</span>
          </nav>
        </DashboardSection>
      </header>

      <div className="flex-1 overflow-auto bg-slate-50/30 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm">
                <Truck className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter font-mono">{vehicle.id}</h1>
                <p className="text-brand-blue font-bold mt-1 tracking-widest uppercase text-xs">{vehicle.plateNumber}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase tracking-widest shadow-sm border ${getStatusColor(vehicle.status)}`}>
              {getStatusIcon(vehicle.status)}
              {vehicle.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
             <div className="md:col-span-2 space-y-6">
                <InfoCard
                  title="Asset Diagnostics"
                  icon={Activity}
                  items={[
                    { label: "Model / Asset Type", value: vehicle.model },
                    { label: "Operating Hours", value: `${vehicle.operatingHours.toLocaleString()} hrs`, className: "font-mono" }
                  ]}
                >
                   <div className="mt-8 pt-8 border-t border-slate-100 dark:border-slate-800">
                      <div className="flex justify-between items-center mb-4">
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Telemetry Signal Status</p>
                        <SignalHigh className={cn(
                          "w-5 h-5",
                          vehicle.signal === 'Strong' ? 'text-brand-teal' :
                          vehicle.signal === 'Medium' ? 'text-amber-500' :
                          'text-red-500'
                        )} />
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xl font-bold text-slate-900 dark:text-white">{vehicle.signal}</span>
                        <div className="flex gap-1">
                          {[1, 2, 3].map(i => (
                            <div key={i} className={cn(
                              "w-1.5 h-4 rounded-full",
                              i === 1 && "bg-brand-teal",
                              i === 2 && (vehicle.signal === 'Strong' || vehicle.signal === 'Medium' ? "bg-brand-teal" : "bg-slate-200"),
                              i === 3 && (vehicle.signal === 'Strong' ? "bg-brand-teal" : "bg-slate-200")
                            )} />
                          ))}
                        </div>
                      </div>
                   </div>
                </InfoCard>

                <InfoCard
                  title="Current Context"
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
                    { 
                      label: "Last Known Location", 
                      value: vehicle.location || 'Location unavailable',
                      icon: Navigation
                    }
                  ]}
                />
             </div>

             <div className="md:col-span-1 space-y-6">
                <InfoCard
                  title="Maintenance Hub"
                  icon={Wrench}
                >
                   <div className="flex flex-col items-center justify-center py-8 text-center opacity-40">
                      <div className="w-16 h-16 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center mb-4">
                        <Truck className="w-6 h-6 text-slate-400" />
                      </div>
                      <p className="text-[10px] font-bold text-slate-500 uppercase tracking-tight">No active faults</p>
                      <p className="text-xs text-slate-400 mt-2">Fleet health is optimal.</p>
                   </div>
                </InfoCard>

                <MetricCard
                  label="Health Score"
                  value="98"
                  icon={Activity}
                  iconColor="text-brand-teal"
                  subValue="Optimal Performance"
                />
             </div>
          </div>
        </DashboardSection>
      </div>
    </div>
  );
}
