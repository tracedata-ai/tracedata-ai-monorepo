"use client";

import { useState } from "react";
import { dashboardConfig, DriverProfile } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { driverColumns } from "./driver-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";
import { cn } from "@/lib/utils";
import { Activity, ShieldAlert, Award, BrainCircuit, Search, UserCheck, Trash2 } from "lucide-react";

function DriverDetailContent({ driver }: { driver: DriverProfile }) {
  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-6 border-b border-border">
         <div className="flex items-center gap-4 mb-4">
           <div className="w-12 h-12 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10 shadow-sm font-black text-xl">
             {driver.name.split(' ').map(n => n[0]).join('')}
           </div>
           <div>
             <h4 className="text-xl font-black text-foreground tracking-tight leading-tight">{driver.name}</h4>
             <p className="text-[10px] text-brand-blue font-bold tracking-widest uppercase font-mono mt-1">{driver.id}</p>
           </div>
         </div>
         
         <div className="grid grid-cols-2 gap-4">
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
       </DashboardSection>

      <div className="p-6 space-y-6">
        <InfoCard
          title="Aggregate Metrics"
          icon={Activity}
          items={[
            { label: "Trips Completed", value: driver.tripsCompleted },
            { 
              label: "Rating", 
              value: (
                <div className="flex items-center gap-1.5 ">
                  {driver.rating.toFixed(1)} <Award className="w-4 h-4 text-amber-500" />
                </div>
              )
            }
          ]}
        />

        <InfoCard
          title="Compliance Audit"
          icon={ShieldAlert}
          items={[
            { 
              label: "License", 
              value: (
                <span className={`text-xs font-bold px-3 py-1 rounded-full border ${
                  driver.licenseStatus === "Valid" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
                  driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-100" :
                  "bg-rose-50 text-rose-600 border-rose-100"
                }`}>{driver.licenseStatus}</span>
              )
            },
            { 
              label: "Recent Incidents", 
              value: driver.recentIncidents,
              className: driver.recentIncidents > 0 ? "text-rose-500" : "text-emerald-500"
            }
          ]}
        />

        {driver.explanation && (
          <FeatureCard
            title="Behavioral DNA"
            icon={BrainCircuit}
            variant="brand"
            isNarrative
          >
            {driver.explanation.humanSummary}
            
            <div className="mt-8 space-y-6">
              <div className="space-y-4">
                <p className="text-xs text-brand-blue uppercase font-bold tracking-widest">Feature Significance</p>
                {Object.entries(driver.explanation.featureImportance).map(([feature, value]) => (
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
                <p className="text-sm font-bold text-slate-900 font-mono">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
              </div>
            </div>
          </FeatureCard>
        )}
      </div>
    </div>
  );
}

export default function DriversPage() {
  const { drivers } = dashboardConfig;
  const [selectedDriverId, setSelectedDriverId] = useState<string | null>(null);
  const selectedDriver = drivers.find(d => d.id === selectedDriverId) || null;

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="drivers-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border flex-shrink-0">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Driver Operations</h2>
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
        </DashboardSection>
      </header>

      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-8">
          <DataTable
            columns={driverColumns}
            data={drivers}
            selectedId={selectedDriverId}
            onRowClick={(driver) => setSelectedDriverId(driver.id)}
          />
        </DashboardSection>
      </main>

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
