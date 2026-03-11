"use client";

import { useState } from "react";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
import { Route, Clock, CheckCircle2, Search, ShieldCheck, BrainCircuit } from "lucide-react";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { tripColumns, formatTripMins } from "./trip-columns";

function TripDetailContent({ trip }: { trip: TripRecord }) {
  return (
    <>
      <div className="px-6 pb-4 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
            <Route className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-foreground text-lg leading-tight font-mono">{trip.id}</h4>
            <p className="text-xs text-muted-foreground mt-1">
              Started: {new Date(trip.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Status</p>
            <p className={`text-sm font-bold uppercase ${
              trip.status === "In Progress" ? "text-brand-blue" :
              trip.status === "Completed" ? "text-brand-teal" :
              trip.status === "Scheduled" ? "text-slate-600 dark:text-slate-400" :
              "text-red-500"
            }`}>{trip.status}</p>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Route Template</p>
            <p className="text-sm font-bold text-foreground font-mono">{trip.routeId}</p>
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
                  {trip.actualDurationMins ? formatTripMins(trip.actualDurationMins) : '--'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Hist. Avg Baseline</p>
                <p className="text-xl font-bold text-foreground mt-1 text-slate-400">
                  {formatTripMins(trip.historicalAvgMins)}
                </p>
              </div>
            </div>
            {trip.actualDurationMins && (
              <div className={`text-xs font-bold p-2 text-center rounded border ${
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
        </div>

        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-brand-teal" /> Safety & Performance
          </h5>
          <div className="bg-brand-teal/5 p-4 rounded-xl border border-brand-teal/20 flex justify-between items-center">
            <p className="text-xs text-brand-teal uppercase font-bold tracking-wider">Dynamic Score</p>
            <p className="text-2xl font-black text-brand-teal">
              {trip.score !== undefined ? trip.score : '--'}
            </p>
          </div>
        </div>

        {trip.explanation && (
          <div>
            <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-purple-500" /> Behavior Analysis (XAI)
            </h5>
            <div className="bg-purple-500/5 p-4 rounded-xl border border-purple-500/20 space-y-4">
              <p className="text-xs text-muted-foreground italic leading-relaxed">
                "{trip.explanation.humanSummary}"
              </p>
              
              <div className="space-y-3">
                <p className="text-[10px] text-purple-500 uppercase font-bold tracking-wider">Feature Importance (SHAP/LIME)</p>
                {Object.entries(trip.explanation.featureImportance).map(([feature, value]) => (
                  <div key={feature} className="space-y-1">
                    <div className="flex justify-between text-[10px] items-center">
                      <span className="text-muted-foreground font-mono uppercase">{feature.replace('_', ' ')}</span>
                      <span className={`font-bold ${value >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {value >= 0 ? '+' : ''}{(value * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden flex">
                      <div 
                        className={`h-full rounded-full transition-all ${value >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                        style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-purple-500/10 flex justify-between items-center">
                <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Fairness Audit Score (SPD)</p>
                <p className="text-xs font-bold text-foreground font-mono">{trip.explanation.fairnessAuditScore.toFixed(3)}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default function TripsPage() {
  const { trips } = dashboardConfig;
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const selectedTrip = trips.find(t => t.id === selectedTripId) || null;

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
              <input type="text" placeholder="Search by Trip ID or Route..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
            </div>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">New Dispatch</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Route className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">In Progress</span>
            <span className="text-3xl font-bold text-foreground">{trips.filter(t => t.status === "In Progress").length}</span>
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
        <DataTable
          columns={tripColumns}
          data={trips}
          selectedId={selectedTripId}
          onRowClick={(trip) => setSelectedTripId(trip.id)}
        />
      </div>

      <DetailSheet
        isOpen={!!selectedTripId}
        onClose={() => setSelectedTripId(null)}
        title="Trip Details"
        deepLink={selectedTrip ? `/dashboard/trips/${selectedTrip.id}` : undefined}
      >
        {selectedTrip && <TripDetailContent trip={selectedTrip} />}
      </DetailSheet>
    </div>
  );
}
