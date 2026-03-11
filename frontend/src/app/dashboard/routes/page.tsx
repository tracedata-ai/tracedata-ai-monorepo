"use client";

import { useState } from "react";
import Link from "next/link";
import { Map, Search, ArrowRight, Route, BarChart3, ExternalLink, Activity, Target } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export default function RoutesPage() {
  const { routes } = dashboardConfig;
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);

  const selectedRoute = routes.find(r => r.id === selectedRouteId) || null;

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

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
              <input 
                type="text" 
                placeholder="Search origin or destination..." 
                className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue"
              />
            </div>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
              Generate Route
            </button>
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
            <span className="text-3xl font-bold text-foreground">
              {routes.reduce((acc, route) => acc + route.totalTripsCompleted, 0).toLocaleString()}
            </span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <BarChart3 className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Optimization Engine</span>
            <span className="text-xl font-bold text-foreground mt-1 text-amber-500 flex items-center gap-1">
              Running <span className="relative flex h-3 w-3"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span></span>
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-border overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-slate-800/50">
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Route ID</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Path Details</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Hist. Avg Time</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Std Distance</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trips Run</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-border">
              {routes.map((route) => (
                <TableRow 
                  key={route.id} 
                  onClick={() => setSelectedRouteId(route.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedRouteId === route.id ? "bg-brand-blue/5" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell className="px-6 py-4">
                    <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-brand-blue/10 text-brand-blue border border-brand-blue/20">
                      {route.id}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className="font-bold text-foreground text-sm">{route.name}</span>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span className="truncate max-w-[150px]">{route.origin}</span>
                        <ArrowRight className="w-3 h-3 text-brand-teal shrink-0" />
                        <span className="truncate max-w-[150px]">{route.destination}</span>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="font-medium text-foreground">{formatMinsToHours(route.historicalAvgMins)}</span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="font-medium text-foreground">{route.standardDistanceKm.toFixed(1)} km</span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="font-mono font-medium text-brand-teal">{route.totalTripsCompleted.toLocaleString()}</span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!selectedRouteId} onOpenChange={(open) => !open && setSelectedRouteId(null)}>
        <SheetContent className="w-full sm:max-w-md bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-xl">
          <SheetHeader className="sr-only">
            <SheetTitle>Route Details</SheetTitle>
          </SheetHeader>
          
          {selectedRoute && (
            <div className="flex flex-col h-full mt-8">
              <div className="p-6 pt-2 border-b border-border">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-foreground tracking-tight">Route Details</h3>
                  <Link 
                    href={`/dashboard/routes/${selectedRoute.id}`}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-blue bg-brand-blue/10 hover:bg-brand-blue/20 px-3 py-1.5 rounded-md transition-colors"
                  >
                    Open Page <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
                    <Map className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground text-lg leading-tight">{selectedRoute.name}</h4>
                    <p className="text-xs text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">{selectedRoute.id}</p>
                  </div>
                </div>

                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4 border border-border">
                   <div className="flex items-center gap-3">
                     <div className="w-2 h-2 rounded-full bg-slate-300 dark:bg-slate-600"></div>
                     <p className="text-sm font-medium text-foreground">{selectedRoute.origin}</p>
                   </div>
                   <div className="ml-[3px] border-l-2 border-dashed border-slate-300 dark:border-slate-600 h-6 my-1"></div>
                   <div className="flex items-center gap-3">
                     <div className="w-2 h-2 rounded-full bg-brand-teal"></div>
                     <p className="text-sm font-medium text-foreground">{selectedRoute.destination}</p>
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
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Time</p>
                      <p className="text-lg font-bold text-foreground mt-1">
                        {formatMinsToHours(selectedRoute.historicalAvgMins)}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Distance</p>
                      <p className="text-lg font-bold text-foreground mt-1">
                        {selectedRoute.standardDistanceKm.toFixed(1)} km
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Target className="w-4 h-4 text-brand-teal" /> Usage Frequency
                  </h5>
                  <div className="bg-brand-teal/5 p-4 rounded-xl border border-brand-teal/20 flex justify-between items-center">
                    <p className="text-xs text-brand-teal uppercase font-bold tracking-wider">Total Trips Run</p>
                    <p className="text-xl font-bold font-mono text-brand-teal">
                      {selectedRoute.totalTripsCompleted.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
