"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  UserCheck,
  ShieldAlert,
  Award,
  Activity,
  FileCheck2,
  AlertTriangle
} from "lucide-react";

export default function DriverDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const driverId = resolvedParams.id;
  
  const driver = dashboardConfig.drivers.find((d) => d.id === driverId);
  
  if (!driver) {
    notFound();
  }

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <Link href="/dashboard/drivers" className="hover:text-brand-blue hover:bg-brand-blue/5 px-2 py-1 rounded transition-colors flex items-center gap-1.5 -ml-2">
            <ArrowLeft className="w-4 h-4" />
            Drivers Hub
          </Link>
          <ChevronRight className="w-4 h-4 mx-3" />
          <span className="text-foreground">{driver.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-2xl shadow-sm border border-brand-blue/20">
                {driver.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h1 className="text-3xl font-black text-foreground tracking-tight">{driver.name}</h1>
                <p className="text-brand-blue font-bold mt-1 font-mono">{driver.id}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-sm font-bold uppercase border shadow-sm ${
                 driver.status === "Active"
                 ? "bg-brand-teal/10 text-brand-teal border-brand-teal/20"
                 : driver.status === "On Break" 
                 ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
                 : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
             }`}>
              {driver.status === "Active" && <div className="w-2 h-2 rounded-full bg-brand-teal animate-pulse"></div>}
              {driver.status === "On Break" && <div className="w-2 h-2 rounded-full bg-amber-500"></div>}
              {driver.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Activity className="w-4 h-4 text-brand-blue" />
                     Performance Analytics
                   </h3>
                   
                   <div className="grid grid-cols-2 gap-6">
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-xl border border-border">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Trips Completed</p>
                         <p className="text-3xl font-black text-foreground mt-2 font-mono flex items-baseline gap-2">
                           {driver.tripsCompleted}
                           <span className="text-sm text-green-500 font-bold uppercase tracking-wider flex items-center">
                             +12% <span className="text-xs text-muted-foreground ml-1">vs avg</span>
                           </span>
                         </p>
                      </div>
                      
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-xl border border-border">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Customer Rating</p>
                         <p className="text-3xl font-black text-foreground mt-2 flex items-center gap-2">
                           {driver.rating.toFixed(1)}
                           <Award className="w-6 h-6 text-amber-500" />
                         </p>
                      </div>

                      <div className="col-span-2 bg-gradient-to-br from-brand-teal/5 to-transparent dark:from-brand-teal/10 p-6 rounded-xl border border-brand-teal/20">
                        <div className="flex justify-between items-center mb-2">
                           <p className="text-xs text-brand-teal uppercase font-bold tracking-widest">Aggregate Trip Score</p>
                           <p className="text-3xl font-black text-brand-teal">{driver.avgTripScore}</p>
                        </div>
                        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mb-2">
                           <div className="bg-brand-teal h-2 rounded-full" style={{ width: `${driver.avgTripScore}%` }}></div>
                        </div>
                        <p className="text-xs text-muted-foreground font-medium">Derived from telemetry, routing efficiency, and customer sentiment.</p>
                      </div>
                   </div>
                </div>
             </div>

             <div className="col-span-1 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <ShieldAlert className="w-4 h-4 text-amber-500" />
                     Compliance
                   </h3>
                   
                   <div className="space-y-6">
                      <div>
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-1 mb-2">
                           <FileCheck2 className="w-3 h-3" /> License Status
                         </p>
                         <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold border ${
                            driver.licenseStatus === "Valid" ? "bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400" :
                            driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-400" :
                            "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400"
                         }`}>
                            {driver.licenseStatus}
                         </div>
                      </div>
                      
                      <div className="pt-4 border-t border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-1 mb-2">
                           <AlertTriangle className="w-3 h-3" /> Recent Incidents
                         </p>
                         {driver.recentIncidents === 0 ? (
                           <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded border border-border">
                             <p className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                               <UserCheck className="w-4 h-4 text-green-500" /> Clean record for past 30 days.
                             </p>
                           </div>
                         ) : (
                           <div className="bg-red-50 dark:bg-red-900/10 p-3 rounded border border-red-200 dark:border-red-800/50">
                             <p className="text-xl font-bold text-red-600 dark:text-red-400 font-mono mb-1">{driver.recentIncidents}</p>
                             <p className="text-xs font-bold text-red-800/60 dark:text-red-300">Incidents logged this period.</p>
                           </div>
                         )}
                      </div>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
