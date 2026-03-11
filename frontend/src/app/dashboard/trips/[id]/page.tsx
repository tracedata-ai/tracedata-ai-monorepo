"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  Route,
  Clock,
  ShieldCheck,
  MapPin,
  Car
} from "lucide-react";

export default function TripDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const tripId = resolvedParams.id;
  
  const trip = dashboardConfig.trips.find((t) => t.id === tripId);
  
  if (!trip) {
    notFound();
  }

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "In Progress": return "bg-brand-blue/10 text-brand-blue border border-brand-blue/20";
      case "Completed": return "bg-brand-teal/10 text-brand-teal border border-brand-teal/20";
      case "Scheduled": return "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700";
      case "Cancelled": return "bg-red-50 text-red-600 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800";
      default: return "";
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <Link href="/dashboard/trips" className="hover:text-brand-blue hover:bg-brand-blue/5 px-2 py-1 rounded transition-colors flex items-center gap-1.5 -ml-2">
            <ArrowLeft className="w-4 h-4" />
            Trip Manifest
          </Link>
          <ChevronRight className="w-4 h-4 mx-3" />
          <span className="text-foreground">{trip.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 border-b border-border pb-6">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-xl bg-brand-blue/10 flex items-center justify-center text-brand-blue shadow-sm border border-brand-blue/20">
                <Route className="w-8 h-8" />
              </div>
              <div>
                <h1 className="text-3xl font-black text-foreground tracking-tight font-mono">{trip.id}</h1>
                <p className="text-muted-foreground font-medium mt-1">
                  Started: {new Date(trip.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-lg text-sm font-bold uppercase border shadow-sm ${getStatusColor(trip.status)}`}>
              {trip.status === "In Progress" && <div className="w-2 h-2 rounded-full bg-brand-blue animate-pulse"></div>}
              {trip.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-8">
             <div className="md:col-span-3 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Car className="w-4 h-4 text-brand-blue" />
                     Assignment Details
                   </h3>
                   
                   <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Driver</p>
                         <Link href={`/dashboard/drivers/${trip.driverId}`} className="text-lg font-bold text-brand-blue hover:underline">
                           {trip.driverId}
                         </Link>
                      </div>
                      
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Vehicle</p>
                         <p className="text-lg font-bold text-foreground font-mono">{trip.vehicleId}</p>
                      </div>

                      <div className="col-span-2 bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-1">Route Template</p>
                         <Link href={`/dashboard/routes/${trip.routeId}`} className="text-lg font-bold text-brand-teal hover:underline flex items-center gap-2">
                           <MapPin className="w-4 h-4" /> {trip.routeId}
                         </Link>
                      </div>
                   </div>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Clock className="w-4 h-4 text-brand-blue" />
                     Time & Distance Telemetry
                   </h3>
                   
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                      <div>
                        <div className="flex justify-between items-center mb-4">
                           <div>
                              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Actual Time</p>
                              <p className="text-3xl font-black text-foreground mt-1">
                                 {trip.actualDurationMins ? formatMinsToHours(trip.actualDurationMins) : '--'}
                              </p>
                           </div>
                           <div className="text-right">
                              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Hist. Avg Baseline</p>
                              <p className="text-xl font-bold text-foreground mt-1 text-slate-400">
                                 {formatMinsToHours(trip.historicalAvgMins)}
                              </p>
                           </div>
                        </div>
                        {trip.actualDurationMins && (
                           <div className={`text-sm font-bold p-3 text-center rounded-lg border ${
                              trip.actualDurationMins > trip.historicalAvgMins ? 'bg-amber-50 text-amber-600 border-amber-200 dark:bg-amber-900/20 dark:text-amber-400 dark:border-amber-800' :
                              trip.actualDurationMins < trip.historicalAvgMins ? 'bg-brand-teal/10 text-brand-teal border-brand-teal/20' :
                              'bg-slate-100 text-slate-600 border-slate-200 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400'
                           }`}>
                              {trip.actualDurationMins > trip.historicalAvgMins 
                                 ? `+${Math.round(((trip.actualDurationMins - trip.historicalAvgMins) / trip.historicalAvgMins) * 100)}% slower than average`
                                 : trip.actualDurationMins < trip.historicalAvgMins 
                                 ? `${Math.round(((trip.historicalAvgMins - trip.actualDurationMins) / trip.historicalAvgMins) * 100)}% faster than average`
                                 : 'Right on schedule'}
                           </div>
                        )}
                      </div>

                      <div className="bg-slate-50 dark:bg-slate-800/50 p-6 rounded-xl border border-border flex flex-col justify-center">
                         <div className="flex justify-between items-end mb-3">
                           <div>
                              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Distance Covered</p>
                              <p className="text-2xl font-bold text-foreground font-mono mt-1">{trip.currentDistanceKm?.toFixed(1) || 0} <span className="text-sm text-muted-foreground">km</span></p>
                           </div>
                           <div className="text-right">
                              <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Total Route</p>
                              <p className="text-xl font-bold text-muted-foreground font-mono mt-1">{trip.distanceKm.toFixed(1)} <span className="text-sm">km</span></p>
                           </div>
                         </div>
                         <div className="w-full h-3 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                           <div 
                              className={`h-full rounded-full transition-all ${trip.status === 'Completed' ? 'bg-brand-teal' : 'bg-brand-blue'}`} 
                              style={{ width: `${Math.min(100, ((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)}%` }}
                           />
                         </div>
                      </div>
                   </div>
                </div>
             </div>

             <div className="md:col-span-1 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm flex flex-col h-full bg-gradient-to-b from-brand-teal/5 to-white dark:from-brand-teal/10 dark:to-slate-900">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <ShieldCheck className="w-4 h-4 text-brand-teal" /> Safety & Performance
                   </h3>
                   
                   {trip.status === "Completed" && trip.score !== undefined ? (
                      <div className="flex flex-col items-center justify-center flex-1 py-8 text-center">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest mb-4">Final Trip Score</p>
                         <div className={`w-36 h-36 rounded-full flex items-center justify-center border-8 shadow-inner ${
                            trip.score >= 90 ? 'border-brand-teal/20 text-brand-teal bg-brand-teal/5' : 
                            trip.score >= 70 ? 'border-amber-500/20 text-amber-500 bg-amber-500/5' : 
                            'border-red-500/20 text-red-500 bg-red-500/5'
                         }`}>
                           <span className="text-6xl font-black">{trip.score}</span>
                         </div>
                         <p className="text-xs text-muted-foreground mt-8 leading-relaxed px-4">
                           Score is computed by AI agents analyzing telemetry, route adherence, and context.
                         </p>
                      </div>
                   ) : (
                      <div className="flex flex-col items-center justify-center flex-1 py-8 text-center opacity-60">
                         <div className="w-24 h-24 rounded-full border-4 border-dashed border-slate-300 dark:border-slate-700 flex items-center justify-center mb-4">
                           <ShieldCheck className="w-8 h-8 text-slate-400" />
                         </div>
                         <p className="text-sm font-bold text-muted-foreground">Score pending</p>
                         <p className="text-xs text-muted-foreground mt-2">Available upon trip completion.</p>
                      </div>
                   )}
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
