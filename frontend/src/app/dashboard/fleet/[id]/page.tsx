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
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <Link href="/dashboard/fleet" className="hover:text-brand-blue hover:bg-brand-blue/5 px-2 py-1 rounded transition-colors flex items-center gap-1.5 -ml-2">
            <ArrowLeft className="w-4 h-4" />
            Fleet Telemetry
          </Link>
          <ChevronRight className="w-4 h-4 mx-3" />
          <span className="text-foreground">{vehicle.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-border pb-6">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-xl bg-brand-blue/10 flex items-center justify-center text-brand-blue shadow-sm border border-brand-blue/20">
                <Truck className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-foreground tracking-tight font-mono">{vehicle.id}</h1>
                <p className="text-brand-blue font-bold mt-1 tracking-widest uppercase">{vehicle.plateNumber}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-lg text-sm font-bold uppercase border shadow-sm ${getStatusColor(vehicle.status)}`}>
              {getStatusIcon(vehicle.status)}
              {vehicle.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
             <div className="md:col-span-2 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Activity className="w-4 h-4 text-brand-blue" />
                     Diagnostics & Specifications
                   </h3>
                   
                   <div className="grid grid-cols-2 gap-6">
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Model / Asset Type</p>
                         <p className="text-lg font-bold text-foreground">{vehicle.model}</p>
                      </div>
                      
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Total Operating Hours</p>
                         <p className="text-3xl font-black text-foreground font-mono mt-1">
                           {vehicle.operatingHours.toLocaleString()}<span className="text-sm text-muted-foreground ml-1">hrs</span>
                         </p>
                      </div>

                      <div className="col-span-2 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <div className="flex justify-between items-center mb-2">
                           <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Telemetry Signal Status</p>
                           <SignalHigh className={`w-5 h-5 ${
                              vehicle.signal === 'Strong' ? 'text-brand-teal' :
                              vehicle.signal === 'Medium' ? 'text-amber-500' :
                              'text-red-500'
                           }`} />
                         </div>
                         <div className="flex items-center gap-2">
                           <span className="text-lg font-bold text-foreground">{vehicle.signal}</span>
                           <span className="text-xs font-medium text-muted-foreground ml-2">
                             Connected to Command Center
                           </span>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <MapPin className="w-4 h-4 text-brand-blue" />
                     Current Context
                   </h3>
                   
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="border border-border p-5 rounded-xl">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-2">Assigned Driver</p>
                        {vehicle.driver ? (
                          <Link href={`/dashboard/drivers/${vehicle.driver}`} className="text-xl font-bold text-brand-blue hover:underline">
                             {vehicle.driver}
                          </Link>
                        ) : (
                          <p className="text-lg font-medium text-muted-foreground">Unassigned</p>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">Currently commanding this vehicle.</p>
                      </div>

                      <div className="border border-border p-5 rounded-xl bg-slate-50 dark:bg-slate-800/50">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-2">Last Known Location</p>
                        <p className="text-lg font-bold text-foreground leading-tight">
                           {vehicle.location || 'Location unavailable'}
                        </p>
                        <p className="text-xs text-muted-foreground mt-2 flex items-center gap-1">
                          <MapPin className="w-3 h-3" /> Updated via GPS
                        </p>
                      </div>
                   </div>
                </div>
             </div>

             <div className="md:col-span-1 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm flex flex-col h-full">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Wrench className="w-4 h-4 text-slate-400" /> Active Issues
                   </h3>
                   
                   <div className="flex flex-col items-center justify-center flex-1 py-8 text-center opacity-60">
                      <div className="w-20 h-20 rounded-full border-4 border-dashed border-slate-300 dark:border-slate-700 flex items-center justify-center mb-4">
                        <Truck className="w-8 h-8 text-slate-400" />
                      </div>
                      <p className="text-sm font-bold text-muted-foreground">No active faults</p>
                      <p className="text-xs text-muted-foreground mt-2 px-4">See Issues tab for historical logs.</p>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
