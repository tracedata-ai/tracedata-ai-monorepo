"use client";

import { useState } from "react";
import { dashboardConfig, TripRecord } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { tripColumns, formatTripMins } from "./trip-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Route, Clock, CheckCircle2, Search, BrainCircuit, TrendingUp } from "lucide-react";

function TripDetailContent({ trip }: { trip: TripRecord }) {
  return (
    <DetailContentTemplate
      heroIcon={Route}
      heroTitle={trip.id}
      heroSubtitle={trip.routeId}
      highlights={[
        {
          label: "Live Status",
          value: trip.status,
          className: cn(
            trip.status === "In Progress" ? "text-brand-blue" :
            trip.status === "Completed" ? "text-emerald-500" :
            "text-slate-400"
          )
        },
        {
          label: "Performance Score",
          value: trip.score !== undefined ? trip.score : '--',
          icon: TrendingUp,
          iconColor: "text-emerald-500"
        }
      ]}
    >
      <div className="space-y-6">
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
                      <span className={cn(
                        (value as number) >= 0 ? 'text-emerald-500' : 'text-rose-500'
                      )}>
                        {(value as number) >= 0 ? '+' : ''}{((value as number) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={Math.abs(value as number) * 100} 
                      className={cn(
                        "h-1 transition-all duration-1000",
                        (value as number) >= 0 ? "[&>div]:bg-emerald-500" : "[&>div]:bg-rose-500"
                      )}
                      style={{ marginLeft: (value as number) >= 0 ? '0' : 'auto', width: '100% ' }}
                    />
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
    </DetailContentTemplate>
  );
}

export default function TripsPage() {
  const { trips } = dashboardConfig;
  const [selectedTripId, setSelectedTripId] = useState<string | null>(null);
  const selectedTrip = trips.find(t => t.id === selectedTripId) || null;

  return (
    <DashboardPageTemplate
      title="Trip Manifest"
      description="Monitor active routing, scheduled dispatches, and historical trips."
      headerActions={
        <>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" placeholder="Search by Trip ID or Route..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
          </div>
          <Button>New Dispatch</Button>
        </>
      }
      stats={
        <>
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
        </>
      }
    >
      <DataTable
        columns={tripColumns}
        data={trips}
        selectedId={selectedTripId}
        onRowClick={(trip) => setSelectedTripId(trip.id)}
      />

      <DetailSheet
        isOpen={!!selectedTripId}
        onClose={() => setSelectedTripId(null)}
        title="Trip Details"
        deepLink={selectedTrip ? `/dashboard/trips/${selectedTrip.id}` : undefined}
      >
        {selectedTrip && <TripDetailContent trip={selectedTrip} />}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}
