"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  Map,
  Activity,
  Target
} from "lucide-react";

export default function RouteDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const routeId = resolvedParams.id;
  
  const route = dashboardConfig.routes.find((r) => r.id === routeId);
  
  if (!route) {
    notFound();
  }

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <Link href="/dashboard/routes" className="hover:text-brand-blue hover:bg-brand-blue/5 px-2 py-1 rounded transition-colors flex items-center gap-1.5 -ml-2">
            <ArrowLeft className="w-4 h-4" />
            Route Catalog
          </Link>
          <ChevronRight className="w-4 h-4 mx-3" />
          <span className="text-foreground">{route.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-border pb-6">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-xl bg-brand-blue/10 flex items-center justify-center text-brand-blue shadow-sm border border-brand-blue/20">
                <Map className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-foreground tracking-tight">{route.name}</h1>
                <p className="text-brand-blue font-bold mt-1 font-mono">{route.id}</p>
              </div>
            </div>
            
            <div className="px-4 py-2 flex items-center gap-2 rounded-lg text-sm font-bold uppercase border bg-brand-teal/5 text-brand-teal border-brand-teal/20 shadow-sm">
              <Target className="w-4 h-4" /> Template Active
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest">
                     Path Details
                   </h3>
                   
                   <div className="relative">
                      <div className="absolute left-4 top-4 bottom-4 w-0.5 bg-slate-200 dark:bg-slate-800"></div>
                      
                      <div className="relative flex items-center gap-6 mb-8">
                         <div className="w-8 h-8 rounded-full bg-slate-100 dark:bg-slate-800 border-4 border-white dark:border-slate-900 z-10 flex items-center justify-center">
                            <div className="w-2.5 h-2.5 rounded-full bg-slate-400 dark:bg-slate-500"></div>
                         </div>
                         <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">Origin</p>
                            <p className="text-lg font-bold text-foreground">{route.origin}</p>
                         </div>
                      </div>

                      <div className="relative flex items-center gap-6">
                         <div className="w-8 h-8 rounded-full bg-brand-teal/20 border-4 border-white dark:border-slate-900 z-10 flex items-center justify-center">
                            <div className="w-2.5 h-2.5 rounded-full bg-brand-teal"></div>
                         </div>
                         <div className="flex-1 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                            <p className="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">Destination</p>
                            <p className="text-lg font-bold text-foreground">{route.destination}</p>
                         </div>
                      </div>
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                   <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm flex flex-col justify-center">
                      <p className="text-xs text-slate-500 uppercase font-bold tracking-widest text-center">Historical Average Time</p>
                      <p className="text-4xl font-black text-foreground mt-3 text-center">{formatMinsToHours(route.historicalAvgMins)}</p>
                      <p className="text-xs text-brand-teal font-bold uppercase tracking-wider text-center mt-2 flex items-center justify-center gap-1">
                         <Activity className="w-3 h-3" /> Baseline Stable
                      </p>
                   </div>
                   <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm flex flex-col justify-center">
                      <p className="text-xs text-slate-500 uppercase font-bold tracking-widest text-center">Standard Distance</p>
                      <p className="text-4xl font-black text-foreground mt-3 text-center">{route.standardDistanceKm.toFixed(1)} <span className="text-xl text-muted-foreground">km</span></p>
                      <p className="text-xs text-muted-foreground font-medium text-center mt-2">
                         Optimal path calculated
                      </p>
                   </div>
                </div>
             </div>

             <div className="col-span-1 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm bg-gradient-to-b from-brand-teal/5 to-white dark:from-brand-teal/10 dark:to-slate-900">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Target className="w-4 h-4 text-brand-teal" /> Usage Statistics
                   </h3>
                   
                   <div className="text-center py-6">
                      <p className="text-5xl font-black text-brand-teal font-mono">
                         {route.totalTripsCompleted.toLocaleString()}
                      </p>
                      <p className="text-sm font-bold text-slate-500 uppercase tracking-widest mt-2">Total Trips Run</p>
                   </div>

                   <div className="h-px w-full bg-border my-4"></div>

                   <p className="text-xs text-muted-foreground leading-relaxed">
                     This template is actively used by the dispatch engine for routing. Adjustments to baselines will affect ETA estimations across the fleet.
                   </p>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
