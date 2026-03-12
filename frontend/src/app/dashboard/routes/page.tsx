"use client";

import { useState } from "react";
import { dashboardConfig, RouteRecord } from "@/config/dashboard";
import { Map, Search, Route, BarChart3, Activity, Target, ArrowRight } from "lucide-react";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { routeColumns, formatRouteMins } from "./route-columns";

function RouteDetailContent({ route }: { route: RouteRecord }) {
  return (
    <>
      <div className="px-6 pb-4 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
            <Map className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-foreground text-lg leading-tight">{route.name}</h4>
            <p className="text-xs text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">{route.id}</p>
          </div>
        </div>
        <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-border">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600" />
            <p className="text-sm font-medium text-foreground">{route.origin}</p>
          </div>
          <div className="ml-[3px] border-l-2 border-dashed border-slate-300 dark:border-slate-600 h-6 my-1" />
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-brand-teal" />
            <p className="text-sm font-medium text-foreground">{route.destination}</p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <Activity className="w-4 h-4 text-brand-blue" /> Average Baselines
          </h5>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Time</p>
              <p className="text-lg font-bold text-foreground mt-1">{formatRouteMins(route.historicalAvgMins)}</p>
            </div>
            <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Distance</p>
              <p className="text-lg font-bold text-foreground mt-1">{route.standardDistanceKm.toFixed(1)} km</p>
            </div>
          </div>
        </div>

        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-brand-teal" /> Usage Frequency
          </h5>
          <div className="bg-brand-teal/5 p-4 rounded-xl border border-brand-teal/20 flex justify-between items-center">
            <p className="text-xs text-brand-teal uppercase font-bold tracking-wider">Total Trips Run</p>
            <p className="text-xl font-bold font-mono text-brand-teal">{route.totalTripsCompleted.toLocaleString()}</p>
          </div>
        </div>
      </div>
    </>
  );
}

export default function RoutesPage() {
  const { routes } = dashboardConfig;
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const selectedRoute = routes.find(r => r.id === selectedRouteId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="routes-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">Route Catalog</h2>
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
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Map className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Active Templates</span>
            <span className="text-3xl font-bold text-foreground">{routes.length}</span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Route className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Total Fleet Trips</span>
            <span className="text-3xl font-bold text-foreground">{routes.reduce((acc, r) => acc + r.totalTripsCompleted, 0).toLocaleString()}</span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <BarChart3 className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Optimization Engine</span>
            <span className="text-xl font-bold text-foreground mt-1 text-amber-500 flex items-center gap-1">
              Running{" "}
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500" />
              </span>
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8">
        <DataTable
          columns={routeColumns}
          data={routes}
          selectedId={selectedRouteId}
          onRowClick={(route) => setSelectedRouteId(route.id)}
        />
      </div>

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
