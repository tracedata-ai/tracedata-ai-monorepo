"use client";

import { useState } from "react";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { tripColumns, formatTripMins } from "./trip-columns";
import { GlassCard } from "@/components/shared/GlassCard";
import { MetricCard } from "@/components/shared/MetricCard";
import { cn } from "@/lib/utils";
import { Route, Clock, CheckCircle2, Search, ShieldCheck, BrainCircuit, TrendingUp } from "lucide-react";

function TripDetailContent({ trip }: { trip: TripRecord }) {
  return (
    <div className="p-6 space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <MetricCard
          label="Status"
          value={trip.status}
          className={cn(
            trip.status === "In Progress" ? "text-brand-blue" :
            trip.status === "Completed" ? "text-emerald-500" :
            "text-slate-400"
          )}
        />
        <MetricCard
          label="Route Template"
          value={trip.routeId}
          icon={Route}
        />
      </div>

      <GlassCard className="space-y-6">
        <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
          <Clock className="w-4 h-4 text-brand-blue" />
          Temporal Performance
        </h5>
        
        <div className="grid grid-cols-1 gap-4">
          <div className="flex justify-between items-center p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <div>
              <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Actual Duration</p>
              <p className="text-xl font-black text-slate-900 mt-1 font-mono">
                {trip.actualDurationMins ? formatTripMins(trip.actualDurationMins) : '--'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest">Baseline</p>
              <p className="text-sm font-black text-slate-400 mt-1 font-mono">
                {formatTripMins(trip.historicalAvgMins)}
              </p>
            </div>
          </div>

          {trip.actualDurationMins && (
            <div className={cn(
              "text-[10px] font-black p-3 text-center rounded-2xl border uppercase tracking-widest",
              trip.actualDurationMins > trip.historicalAvgMins 
                ? 'bg-rose-50 text-rose-600 border-rose-100' :
              trip.actualDurationMins < trip.historicalAvgMins 
                ? 'bg-emerald-50 text-emerald-600 border-emerald-100' :
                'bg-slate-50 text-slate-500 border-slate-100'
            )}>
              {trip.actualDurationMins > trip.historicalAvgMins
                ? `Efficiency Lag: +${Math.round(((trip.actualDurationMins - trip.historicalAvgMins) / trip.historicalAvgMins) * 100)}%`
                : trip.actualDurationMins < trip.historicalAvgMins
                ? `Performance Gain: ${Math.round(((trip.historicalAvgMins - trip.actualDurationMins) / trip.historicalAvgMins) * 100)}%`
                : 'Optimal schedule match'}
            </div>
          )}
        </div>
      </GlassCard>

      <MetricCard
        label="Dynamic Performance Score"
        value={trip.score !== undefined ? trip.score : '--'}
        icon={TrendingUp}
        iconColor="text-emerald-500"
        trend={trip.score && trip.score > 90 ? { value: 12, label: "Efficiency", isPositive: true } : undefined}
      />

      {trip.explanation && (
        <GlassCard className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 w-24 h-24 text-brand-blue/[0.03] transform translate-x-8 -translate-y-8 group-hover:scale-110 transition-transform">
            <BrainCircuit className="w-full h-full" />
          </div>
          
          <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-purple-500" /> Behavioral DNA
          </h5>
          
          <div className="space-y-6 relative z-10">
            <p className="text-[11px] font-bold text-slate-900 leading-relaxed italic border-l-2 border-purple-200 pl-4 py-1">
              "{trip.explanation.humanSummary}"
            </p>
            
            <div className="space-y-4">
              <p className="text-[9px] text-purple-500 uppercase font-black tracking-[0.2em]">Feature Significance</p>
              {Object.entries(trip.explanation.featureImportance).map(([feature, value]) => (
                <div key={feature} className="space-y-1.5">
                  <div className="flex justify-between text-[9px] items-end font-black">
                    <span className="text-slate-400 uppercase tracking-tighter">{feature.replace('_', ' ')}</span>
                    <span className={value >= 0 ? 'text-emerald-500' : 'text-rose-500'}>
                      {value >= 0 ? '+' : ''}{(value * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full h-1 bg-slate-100 rounded-full overflow-hidden flex">
                    <div 
                      className={`h-full rounded-full transition-all duration-1000 ${value >= 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                      style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-100 flex justify-between items-center">
              <p className="text-[9px] text-slate-400 uppercase font-black tracking-widest">Fairness Audit</p>
              <p className="text-sm font-black text-slate-900 font-mono">{trip.explanation.fairnessAuditScore.toFixed(3)}</p>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
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
          <MetricCard
            label="In Progress"
            value={trips.filter(t => t.status === "In Progress").length}
            icon={Route}
            iconColor="text-brand-blue"
          />
          <MetricCard
            label="Completed Today"
            value={142}
            icon={CheckCircle2}
            iconColor="text-emerald-500"
            trend={{ value: 8, label: "vs yesterday", isPositive: true }}
          />
          <MetricCard
            label="Avg. Duration"
            value="1h 45m"
            icon={Clock}
            iconColor="text-amber-500"
          />
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
