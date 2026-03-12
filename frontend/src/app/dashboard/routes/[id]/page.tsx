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
  Target,
  ArrowRight,
  Navigation
} from "lucide-react";
import { InfoCard } from "@/components/shared/InfoCard";
import { DashboardSection } from "@/components/shared/DashboardSection";
import { MetricCard } from "@/components/shared/MetricCard";
import { cn } from "@/lib/utils";

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
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden text-slate-900">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-100 flex-shrink-0">
        <DashboardSection gridCols={1} className="py-4">
          <nav className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest">
            <Link href="/dashboard/routes" className="hover:text-brand-blue transition-colors flex items-center gap-1.5 -ml-2 px-2 py-1 rounded-full hover:bg-slate-50">
              <ArrowLeft className="w-3.5 h-3.5" />
              Route Catalog
            </Link>
            <ChevronRight className="w-3.5 h-3.5 mx-3 opacity-30" />
            <span className="text-slate-900 dark:text-slate-100">{route.id}</span>
          </nav>
        </DashboardSection>
      </header>

      <div className="flex-1 overflow-auto bg-slate-50/30 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm">
                <Navigation className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">{route.name}</h1>
                <p className="text-brand-blue font-bold mt-1 uppercase tracking-widest text-xs">{route.id}</p>
              </div>
            </div>
            
            <div className="px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase tracking-widest shadow-sm border bg-emerald-50 text-emerald-600 border-emerald-100">
              <Target className="w-4 h-4" /> Template Active
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <InfoCard
                  title="Path Details"
                  icon={Map}
                >
                   <div className="mt-6 flex flex-col md:flex-row items-center gap-8 md:gap-4">
                      <div className="flex-1 w-full bg-slate-50 dark:bg-slate-800/50 p-6 rounded-3xl border border-slate-100 dark:border-slate-800">
                         <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Origin</p>
                         <p className="text-xl font-bold text-slate-900 dark:text-white">{route.origin}</p>
                      </div>
                      
                      <div className="md:px-2">
                        <ArrowRight className="w-6 h-6 text-brand-blue rotate-90 md:rotate-0" />
                      </div>

                      <div className="flex-1 w-full bg-brand-blue/5 dark:bg-brand-blue/10 p-6 rounded-3xl border border-brand-blue/10 dark:border-brand-blue/20">
                         <p className="text-xs font-bold uppercase tracking-widest text-brand-blue/60 mb-2">Destination</p>
                         <p className="text-xl font-bold text-slate-900 dark:text-white">{route.destination}</p>
                      </div>
                   </div>
                </InfoCard>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                   <MetricCard
                      label="Historical Avg Time"
                      value={formatMinsToHours(route.historicalAvgMins)}
                      icon={Activity}
                      iconColor="text-brand-teal"
                      subValue="Baseline Stable"
                   />
                   <MetricCard
                      label="Standard Distance"
                      value={`${route.standardDistanceKm.toFixed(1)} km`}
                      icon={Map}
                      subValue="Optimal Path Verified"
                   />
                </div>
             </div>

             <div className="col-span-1 space-y-6">
                <InfoCard
                  title="Usage Statistics"
                  icon={Target}
                  variant="brand"
                  items={[
                    { label: "Total Trips Completed", value: route.totalTripsCompleted.toLocaleString(), className: "text-2xl font-black text-brand-teal" }
                  ]}
                >
                   <p className="text-[10px] text-slate-400 leading-relaxed font-medium mt-4 border-t border-brand-teal/10 pt-4">
                      This template is actively used by the dispatch engine for routing. Adjustments to baselines will affect ETA estimations across the fleet.
                   </p>
                </InfoCard>
             </div>
          </div>
        </DashboardSection>
      </div>
    </div>
  );
}
