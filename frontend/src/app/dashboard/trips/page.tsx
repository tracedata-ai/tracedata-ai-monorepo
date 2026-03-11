"use client";

import { Search, Route, Clock, CheckCircle2, MapPin } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";

export default function TripsPage() {
  const { trips } = dashboardConfig;

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
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="trips-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Trip Manifest</h2>
          <p className="text-muted-foreground text-sm">Monitor active routing, scheduled dispatches, and historical trips.</p>
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
          <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm focus:outline-none">
            New Dispatch
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <Route className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">In Progress</span>
          <span className="text-3xl font-bold text-foreground">24</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <CheckCircle2 className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Completed Today</span>
          <span className="text-3xl font-bold text-foreground">142</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <Clock className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Avg. Duration</span>
          <span className="text-3xl font-bold text-foreground">1h 45m</span>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trip ID</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Route</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Assignment</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Time (Est vs Act)</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider w-48">Distance</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Score</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {trips.map((trip) => (
                <tr key={trip.id} className="hover:bg-muted/30 transition-colors group">
                  <td className="px-6 py-4">
                    <span className="font-mono text-sm font-bold text-foreground">{trip.id}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${getStatusColor(trip.status)}`}>
                      {trip.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-3 h-3 text-brand-blue" />
                        <span className="text-foreground">{trip.origin}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="w-3 h-3 text-brand-teal" />
                        <span className="text-muted-foreground">{trip.destination}</span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-foreground">{trip.driverId}</span>
                      <span className="text-xs text-muted-foreground">{trip.vehicleId}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <span className="text-sm font-medium text-foreground">
                        {trip.actualDurationMins ? formatMinsToHours(trip.actualDurationMins) : '--'} / {formatMinsToHours(trip.estimatedDurationMins)}
                      </span>
                      {trip.actualDurationMins && (
                        <span className={`text-xs font-bold ${
                          trip.actualDurationMins > trip.estimatedDurationMins ? 'text-amber-500' :
                          trip.actualDurationMins < trip.estimatedDurationMins ? 'text-brand-teal' :
                          'text-muted-foreground'
                        }`}>
                          {trip.actualDurationMins > trip.estimatedDurationMins 
                            ? `+${Math.round(((trip.actualDurationMins - trip.estimatedDurationMins) / trip.estimatedDurationMins) * 100)}% (Over)`
                            : trip.actualDurationMins < trip.estimatedDurationMins 
                            ? `-${Math.round(((trip.estimatedDurationMins - trip.actualDurationMins) / trip.estimatedDurationMins) * 100)}% (Under)`
                            : 'On Time'}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 w-48">
                    <div className="flex flex-col gap-1.5 w-full">
                      <div className="flex justify-between items-center text-xs font-mono">
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
                  </td>
                  <td className="px-6 py-4">
                    {trip.status === "Completed" && trip.score !== undefined ? (
                      <span className={`text-sm font-bold ${trip.score >= 90 ? 'text-brand-teal' : trip.score >= 70 ? 'text-amber-500' : 'text-red-500'}`}>
                        {trip.score}
                      </span>
                    ) : (
                      <span className="text-sm text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-sm font-bold text-brand-blue hover:underline">Track</button>
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
