"use client";

import { Map, Search, ArrowRight, Route, BarChart3 } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";

export default function RoutesPage() {
  const { routes } = dashboardConfig;

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="routes-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Route Catalog</h2>
          <p className="text-muted-foreground text-sm">Manage standard fleet paths, review historical baselines, and track efficiency.</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search origin or destination..." 
              className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue"
            />
          </div>
          <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm focus:outline-none">
            Generate Route
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <Map className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Active Templates</span>
          <span className="text-3xl font-bold text-foreground">{routes.length}</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <Route className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Total Fleet Trips</span>
          <span className="text-3xl font-bold text-foreground">
            {routes.reduce((acc, route) => acc + route.totalTripsCompleted, 0).toLocaleString()}
          </span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <BarChart3 className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Optimization Engine</span>
          <span className="text-xl font-bold text-foreground mt-1 text-amber-500 flex items-center gap-1">
            Running <span className="relative flex h-3 w-3"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span></span>
          </span>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Route ID</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Path Details</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Hist. Avg Time</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Std Distance</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trips Run</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {routes.map((route) => (
                <tr key={route.id} className="hover:bg-muted/30 transition-colors group">
                  <td className="px-6 py-4">
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-brand-blue/10 text-brand-blue border border-brand-blue/20">
                      {route.id}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className="font-bold text-foreground text-sm">{route.name}</span>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="truncate max-w-[150px]">{route.origin}</span>
                        <ArrowRight className="w-3 h-3 text-brand-teal shrink-0" />
                        <span className="truncate max-w-[150px]">{route.destination}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-foreground">{formatMinsToHours(route.historicalAvgMins)}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-medium text-foreground">{route.standardDistanceKm.toFixed(1)} km</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono font-medium text-brand-teal">{route.totalTripsCompleted.toLocaleString()}</span>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-sm font-bold text-brand-blue hover:underline">Edit Route</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
