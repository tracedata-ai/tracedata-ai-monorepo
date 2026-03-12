"use client";

import { useState } from "react";
import { dashboardConfig, RouteRecord } from "@/config/dashboard";
import { Map, Search, Route, BarChart3, Activity, Target, ArrowRight, ShieldCheck, TrendingUp } from "lucide-react";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { routeColumns, formatRouteMins } from "./route-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";

function RouteDetailContent({ route }: { route: RouteRecord }) {
  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-6 border-b border-border">
         <div className="flex items-center gap-4 mb-4">
           <div className="w-12 h-12 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm">
             <Map className="w-6 h-6" />
           </div>
           <div>
             <h4 className="text-xl font-black text-foreground tracking-tight leading-tight">{route.name}</h4>
             <p className="text-[10px] text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">{route.id}</p>
           </div>
         </div>
         <div className="bg-slate-50 dark:bg-slate-800/50 rounded-2xl p-4 border border-border">
           <div className="flex items-center gap-3">
             <div className="w-2 h-2 rounded-full bg-slate-400 dark:bg-slate-600 shadow-sm" />
             <p className="text-xs font-bold text-foreground uppercase tracking-tight">{route.origin}</p>
           </div>
           <div className="ml-[3px] border-l-2 border-dashed border-slate-300 dark:border-slate-700 h-6 my-1" />
           <div className="flex items-center gap-3">
             <div className="w-2 h-2 rounded-full bg-brand-teal shadow-sm shadow-brand-teal/20" />
             <p className="text-xs font-bold text-foreground uppercase tracking-tight">{route.destination}</p>
           </div>
         </div>
       </DashboardSection>

      <div className="p-6 space-y-6">
        <InfoCard
          title="Average Baselines"
          icon={Activity}
          items={[
            { label: "Est. Time", value: formatRouteMins(route.historicalAvgMins) },
            { label: "Standard Distance", value: `${route.standardDistanceKm.toFixed(1)} km` }
          ]}
        />

        <MetricCard
          label="Total Trips Run"
          value={route.totalTripsCompleted.toLocaleString()}
          icon={Target}
          iconColor="text-brand-teal"
        />
      </div>
    </div>
  );
}

export default function RoutesPage() {
  const { routes } = dashboardConfig;
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const selectedRoute = routes.find(r => r.id === selectedRouteId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="routes-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border flex-shrink-0">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Route Catalog</h2>
              <p className="text-muted-foreground mt-1 text-sm">Manage standard fleet paths, review historical baselines, and track efficiency.</p>
            </div>
            <div className="flex gap-3">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input type="text" placeholder="Search origin or destination..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
              </div>
              <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">Generate Route</button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            <MetricCard
              label="Active Templates"
              value={routes.length}
              icon={Map}
              iconColor="text-brand-blue"
            />
            <MetricCard
              label="Total Fleet Trips"
              value={routes.reduce((acc, r) => acc + r.totalTripsCompleted, 0).toLocaleString()}
              icon={Route}
              iconColor="text-brand-teal"
            />
            <MetricCard
              label="Optimization Status"
              value="Running"
              icon={BarChart3}
              iconColor="text-amber-500"
              trend={{ value: 100, label: "AI active", isPositive: true }}
            />
          </div>
        </DashboardSection>
      </header>

      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-8">
          <DataTable
            columns={routeColumns}
            data={routes}
            selectedId={selectedRouteId}
            onRowClick={(route) => setSelectedRouteId(route.id)}
          />
        </DashboardSection>
      </main>

      <DetailSheet
        isOpen={!!selectedRouteId}
        onClose={() => setSelectedRouteId(null)}
        title="Route Details"
        deepLink={selectedRoute ? `/dashboard/routes/${selectedRoute.id}` : undefined}
      >
        {selectedRoute && <RouteDetailContent route={selectedRoute} />}
      </DetailSheet>
    </div>
  );
}
