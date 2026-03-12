"use client";

import { useState } from "react";
import { dashboardConfig, DriverProfile } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { driverColumns } from "./driver-columns";
import { GlassCard } from "@/components/shared/GlassCard";
import { MetricCard } from "@/components/shared/MetricCard";
import { cn } from "@/lib/utils";
import { Activity, ShieldAlert, Award, BrainCircuit, Search, UserCheck } from "lucide-react";

function DriverDetailContent({ driver }: { driver: DriverProfile }) {
  return (
    <div className="p-6 space-y-6">
      <div className="space-y-4">
        <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] px-1 flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-emerald-500" />
          Operator Identity
        </h5>
        <div className="grid grid-cols-2 gap-4 auto-rows-fr">
          <MetricCard
            compact
            label="Current Status"
            value={driver.status}
            className={cn(
              driver.status === 'Active' ? 'text-emerald-600' :
              driver.status === 'On Break' ? 'text-amber-500' :
              'text-slate-400'
            )}
          />
          <MetricCard
            compact
            label="Avg. Score"
            value={driver.avgTripScore}
            icon={Award}
            iconColor="text-emerald-500"
          />
        </div>
      </div>

      <GlassCard compact className="space-y-6">
        <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
          <Activity className="w-4 h-4 text-brand-blue" />
          Aggregate metrics
        </h5>
        <div className="grid grid-cols-1 gap-4">
          <div className="flex justify-between items-center p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Trips Completed</p>
            <p className="text-sm font-black font-mono text-slate-900">{driver.tripsCompleted}</p>
          </div>
          <div className="flex justify-between items-center p-4 bg-slate-50/50 rounded-2xl border border-slate-100">
            <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Rating</p>
            <div className="flex items-center gap-1.5 text-sm font-black text-brand-blue">
              {driver.rating.toFixed(1)} <Award className="w-4 h-4 text-amber-500" />
            </div>
          </div>
        </div>
      </GlassCard>

      <GlassCard compact className="space-y-6">
        <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-500" />
          Compliance Audit
        </h5>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">License</p>
            <span className={`text-[10px] font-black px-3 py-1 rounded-full border ${
              driver.licenseStatus === "Valid" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
              driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-100" :
              "bg-rose-50 text-rose-600 border-rose-100"
            }`}>{driver.licenseStatus}</span>
          </div>
          <div className="flex justify-between items-center">
            <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest">Recent Incidents</p>
            <p className={`text-sm font-black font-mono ${driver.recentIncidents > 0 ? "text-rose-500" : "text-emerald-500"}`}>
              {driver.recentIncidents}
            </p>
          </div>
        </div>
      </GlassCard>

      {driver.explanation && (
        <GlassCard compact className="relative overflow-hidden group">
          <div className="absolute right-0 top-0 w-24 h-24 text-brand-blue/[0.03] transform translate-x-8 -translate-y-8 group-hover:scale-110 transition-transform">
            <BrainCircuit className="w-full h-full" />
          </div>
          
          <h5 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-purple-500" /> Behavioral DNA
          </h5>
          
          <div className="space-y-6 relative z-10">
            <p className="text-[11px] font-bold text-slate-900 leading-relaxed italic border-l-2 border-purple-200 pl-4 py-1">
              "{driver.explanation.humanSummary}"
            </p>
            
            <div className="space-y-4">
              <p className="text-[9px] text-purple-500 uppercase font-black tracking-[0.2em]">Feature Significance</p>
              {Object.entries(driver.explanation.featureImportance).map(([feature, value]) => (
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
              <p className="text-sm font-black text-slate-900 font-mono">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
            </div>
          </div>
        </GlassCard>
      )}
    </div>
  );
}

export default function DriversPage() {
  const { drivers } = dashboardConfig;
  const [selectedDriverId, setSelectedDriverId] = useState<string | null>(null);
  const selectedDriver = drivers.find(d => d.id === selectedDriverId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="drivers-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">Driver Operations</h2>
            <p className="text-muted-foreground mt-1 text-sm">Manage fleet drivers, view shift compliance, and monitor performance.</p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input type="text" placeholder="Search drivers..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
            </div>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">Add Driver</button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <MetricCard
            label="Active Shift"
            value={drivers.filter(d => d.status === "Active").length}
            icon={UserCheck}
            iconColor="text-emerald-500"
          />
          <MetricCard
            label="Compliance Flags"
            value={drivers.reduce((acc, curr) => acc + curr.recentIncidents, 0)}
            icon={ShieldAlert}
            iconColor="text-amber-500"
          />
          <MetricCard
            label="Avg. Fleet Rating"
            value={(drivers.reduce((acc, curr) => acc + curr.rating, 0) / drivers.length).toFixed(1)}
            icon={Award}
            iconColor="text-brand-blue"
          />
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8">
        <DataTable
          columns={driverColumns}
          data={drivers}
          selectedId={selectedDriverId}
          onRowClick={(driver) => setSelectedDriverId(driver.id)}
        />
      </div>

      <DetailSheet
        isOpen={!!selectedDriverId}
        onClose={() => setSelectedDriverId(null)}
        title="Driver Details"
        deepLink={selectedDriver ? `/dashboard/drivers/${selectedDriver.id}` : undefined}
      >
        {selectedDriver && <DriverDetailContent driver={selectedDriver} />}
      </DetailSheet>
    </div>
  );
}
