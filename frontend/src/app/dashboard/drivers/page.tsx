"use client";

import { useState } from "react";
import { dashboardConfig, DriverProfile } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { driverColumns } from "./driver-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Activity, ShieldAlert, Award, BrainCircuit, Search, UserCheck, User } from "lucide-react";
import { Progress } from "@/components/ui/progress";

function DriverDetailContent({ driver }: { driver: DriverProfile }) {
  return (
    <DetailContentTemplate
      heroIcon={User}
      heroTitle={driver.name}
      heroSubtitle={driver.id}
      highlights={[
        {
          label: "Current Status",
          value: driver.status,
          className: cn(
            driver.status === 'Active' ? 'text-emerald-600' :
            driver.status === 'On Break' ? 'text-amber-500' :
            'text-slate-400'
          )
        },
        {
          label: "Avg. Score",
          value: driver.avgTripScore,
          icon: Award,
          iconColor: "text-emerald-500"
        }
      ]}
    >
      <div className="space-y-6">
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
                      style={{ marginLeft: (value as number) >= 0 ? '0' : 'auto', width: '100%' }}
                    />
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
    </DetailContentTemplate>
  );
}

export default function DriversPage() {
  const { drivers } = dashboardConfig;
  const [selectedDriverId, setSelectedDriverId] = useState<string | null>(null);
  const selectedDriver = drivers.find(d => d.id === selectedDriverId) || null;

  return (
    <DashboardPageTemplate
      title="Driver Operations"
      description="Manage fleet drivers, view shift compliance, and monitor performance."
      headerActions={
        <>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" placeholder="Search drivers..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
          </div>
          <Button>Add Driver</Button>
        </>
      }
      stats={
        <>
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
            value={(drivers.reduce((acc: number, curr) => acc + curr.rating, 0) / drivers.length).toFixed(1)}
            icon={Award}
            iconColor="text-brand-blue"
          />
        </>
      }
    >
      <DataTable
        columns={driverColumns}
        data={drivers}
        selectedId={selectedDriverId}
        onRowClick={(driver) => setSelectedDriverId(driver.id)}
      />

      <DetailSheet
        isOpen={!!selectedDriverId}
        onClose={() => setSelectedDriverId(null)}
        title="Driver Details"
        deepLink={selectedDriver ? `/dashboard/drivers/${selectedDriver.id}` : undefined}
      >
        {selectedDriver && <DriverDetailContent driver={selectedDriver} />}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}
