"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, Route, Clock, CheckCircle2, MapPin, ExternalLink, Activity, ArrowRight, ShieldCheck, Map } from "lucide-react";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
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

export default function TripsPage() {
  const { trips } = dashboardConfig;
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);

  const selectedTrip = trips.find((t) => t.id === selectedTripId) || null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "In Progress": return "bg-brand-blue/10 text-brand-blue border border-brand-blue/20";
      case "Completed": return "bg-brand-teal/10 text-brand-teal border border-brand-teal/20";
      case "Scheduled": return "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700";
      case "Cancelled": return "bg-red-500/10 text-red-500 border border-red-500/20";
      default: return "";
    }
  };

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="trips-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">Trip Manifest</h2>
            <p className="text-muted-foreground mt-1 text-sm">Monitor active routing, scheduled dispatches, and historical trips.</p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input 
                type="text" 
                placeholder="Search by Trip ID or Route..." 
                className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue"
              />
            </div>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
              New Dispatch
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Route className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">In Progress</span>
            <span className="text-3xl font-bold text-foreground">
              {trips.filter(t => t.status === "In Progress").length}
            </span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <CheckCircle2 className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Completed Today</span>
            <span className="text-3xl font-bold text-foreground">142</span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Clock className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Avg. Duration</span>
            <span className="text-3xl font-bold text-foreground">1h 45m</span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-border overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-slate-800/50">
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trip ID</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Route</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Assignment</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Distance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-border">
              {trips.map((trip) => (
                <TableRow 
                  key={trip.id} 
                  onClick={() => setSelectedTripId(trip.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedTripId === trip.id ? "bg-brand-blue/5" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell className="px-6 py-4">
                    <span className="font-mono text-sm font-bold text-foreground">{trip.id}</span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${getStatusColor(trip.status)}`}>
                      {trip.status}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-2 text-sm font-bold text-brand-blue/80">
                      <Route className="w-4 h-4" />
                      <span>{trip.routeId}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-bold text-foreground">{trip.driverId}</span>
                      <span className="text-xs text-muted-foreground font-mono">{trip.vehicleId}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4 min-w-[200px]">
                    <div className="flex flex-col gap-1.5 w-full">
                      <div className="flex justify-between items-center text-xs font-mono font-bold">
                        <span className="text-foreground">{trip.currentDistanceKm?.toFixed(1) || 0}km</span>
                        <span className="text-muted-foreground">{trip.distanceKm.toFixed(1)}km</span>
                      </div>
                      <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all ${trip.status === 'Completed' ? 'bg-brand-teal' : 'bg-brand-blue'}`} 
                          style={{ width: `${Math.min(100, ((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)}%` }}
                        />
                      </div>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!selectedTripId} onOpenChange={(open) => !open && setSelectedTripId(null)}>
        <SheetContent className="w-full sm:max-w-md bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-xl">
          <SheetHeader className="sr-only">
            <SheetTitle>Trip Details</SheetTitle>
          </SheetHeader>
          
          {selectedTrip && (
            <div className="flex flex-col h-full mt-8">
              <div className="p-6 pt-2 border-b border-border">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-foreground tracking-tight">Trip Details</h3>
                  <Link 
                    href={`/dashboard/trips/${selectedTrip.id}`}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-blue bg-brand-blue/10 hover:bg-brand-blue/20 px-3 py-1.5 rounded-md transition-colors"
                  >
                    Open Page <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
                    <Route className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground text-lg leading-tight font-mono">{selectedTrip.id}</h4>
                    <p className="text-xs text-muted-foreground mt-1">Started: {new Date(selectedTrip.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Status</p>
                    <p className={`text-sm font-bold uppercase ${
                      selectedTrip.status === "In Progress" ? "text-brand-blue" :
                      selectedTrip.status === "Completed" ? "text-brand-teal" :
                      selectedTrip.status === "Scheduled" ? "text-slate-600 dark:text-slate-400" :
                      "text-red-500"
                    }`}>
                      {selectedTrip.status}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Route Template</p>
                    <p className="text-sm font-bold text-foreground font-mono">
                      {selectedTrip.routeId}
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Clock className="w-4 h-4 text-brand-blue" /> Actual vs Expected
                  </h5>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                    <div className="flex justify-between items-center mb-4">
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Actual Time</p>
                        <p className="text-xl font-bold text-foreground mt-1">
                          {selectedTrip.actualDurationMins ? formatMinsToHours(selectedTrip.actualDurationMins) : '--'}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Hist. Avg Baseline</p>
                        <p className="text-xl font-bold text-foreground mt-1 text-slate-400">
                          {formatMinsToHours(selectedTrip.historicalAvgMins)}
                        </p>
                      </div>
                    </div>
                    {selectedTrip.actualDurationMins && (
                      <div className={`text-xs font-bold p-2 text-center rounded border ${
                        selectedTrip.actualDurationMins > selectedTrip.historicalAvgMins ? 'bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800' :
                        selectedTrip.actualDurationMins < selectedTrip.historicalAvgMins ? 'bg-brand-teal/10 text-brand-teal border-brand-teal/20' :
                        'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'
                      }`}>
                        {selectedTrip.actualDurationMins > selectedTrip.historicalAvgMins 
                          ? `+${Math.round(((selectedTrip.actualDurationMins - selectedTrip.historicalAvgMins) / selectedTrip.historicalAvgMins) * 100)}% slower than average`
                          : selectedTrip.actualDurationMins < selectedTrip.historicalAvgMins 
                          ? `${Math.round(((selectedTrip.historicalAvgMins - selectedTrip.actualDurationMins) / selectedTrip.historicalAvgMins) * 100)}% faster than average`
                          : 'Right on schedule'}
                      </div>
                    )}
                  </div>
                </div>

                <div>
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-brand-teal" /> Safety & Performance
                  </h5>
                  <div className="bg-brand-teal/5 p-4 rounded-xl border border-brand-teal/20 flex justify-between items-center">
                    <p className="text-xs text-brand-teal uppercase font-bold tracking-wider">Dynamic Score</p>
                    <p className="text-2xl font-black text-brand-teal">
                      {selectedTrip.score !== undefined ? selectedTrip.score : '--'}
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
