"use client";

import { useState } from "react";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { tripColumns, formatTripMins } from "./trip-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";
import { cn } from "@/lib/utils";
import { Route, Clock, CheckCircle2, Search, ShieldCheck, BrainCircuit, TrendingUp } from "lucide-react";

function TripDetailContent({ trip }: { trip: TripRecord }) {
  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-6 border-b border-border">
         <div className="flex items-center gap-4 mb-4">
           <div className="w-12 h-12 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm">
             <Route className="w-6 h-6" />
           </div>
           <div>
             <h4 className="text-xl font-black text-foreground tracking-tight leading-tight uppercase font-mono">{trip.id}</h4>
             <p className="text-[10px] text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">{trip.routeId}</p>
           </div>
         </div>
         
         <div className="grid grid-cols-2 gap-4">
           <MetricCard
             compact
             label="Live Status"
             value={trip.status}
             className={cn(
               trip.status === "In Progress" ? "text-brand-blue" :
               trip.status === "Completed" ? "text-emerald-500" :
               "text-slate-400"
             )}
           />
           <MetricCard
             compact
             label="Performance Score"
             value={trip.score !== undefined ? trip.score : '--'}
             icon={TrendingUp}
             iconColor="text-emerald-500"
           />
         </div>
       </DashboardSection>

      <div className="p-6 space-y-6">
        <FeatureCard
          title="Temporal Performance"
          icon={Clock}
        >
          <div className="grid grid-cols-1 gap-4">
            <div className="flex justify-between items-center p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
              <div>
                <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Actual Duration</p>
                <p className="text-xl font-bold text-slate-900 mt-1 font-mono">
                  {trip.actualDurationMins ? formatTripMins(trip.actualDurationMins) : '--'}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 uppercase font-bold tracking-wider">Baseline</p>
                <p className="text-sm font-bold text-slate-400 mt-1 font-mono">
                  {formatTripMins(trip.historicalAvgMins)}
                </p>
              </div>
            </div>

            {trip.actualDurationMins && (
              <div className={cn(
                "text-xs font-bold p-3 text-center rounded-2xl border uppercase tracking-widest",
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
        </FeatureCard>

        <MetricCard
          label="Dynamic Performance Score"
          value={trip.score !== undefined ? trip.score : '--'}
          icon={TrendingUp}
          iconColor="text-emerald-500"
          trend={trip.score && trip.score > 90 ? { value: 12, label: "Efficiency", isPositive: true } : undefined}
        />

        {trip.explanation && (
          <FeatureCard
            title="Behavioral DNA"
            icon={BrainCircuit}
            variant="brand"
            isNarrative
          >
            {trip.explanation.humanSummary}
            
            <div className="mt-8 space-y-6">
              <div className="space-y-4">
                <p className="text-xs text-brand-blue uppercase font-bold tracking-widest">Feature Significance</p>
                {Object.entries(trip.explanation.featureImportance).map(([feature, value]) => (
                  <div key={feature} className="space-y-1.5">
                    <div className="flex justify-between text-xs items-end font-bold">
                      <span className="text-slate-400 uppercase tracking-tight">{feature.replace('_', ' ')}</span>
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
                <p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Fairness Audit</p>
                <p className="text-sm font-bold text-slate-900 font-mono">{trip.explanation.fairnessAuditScore.toFixed(3)}</p>
              </div>
            </div>
          </FeatureCard>
        )}
      </div>
    </div>
  );
}

export default function TripsPage() {
  const { trips } = dashboardConfig;
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const selectedTrip = trips.find(t => t.id === selectedTripId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="trips-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border flex-shrink-0">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Trip Manifest</h2>
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
        </DashboardSection>
      </header>

      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-8">
          <DataTable
            columns={tripColumns}
            data={trips}
            selectedId={selectedTripId}
            onRowClick={(trip) => setSelectedTripId(trip.id)}
          />
        </DashboardSection>
      </main>

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
