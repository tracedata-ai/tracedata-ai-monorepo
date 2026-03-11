"use client";

import { useState } from "react";
import { dashboardConfig, DriverProfile } from "@/config/dashboard";
import { Search, UserCheck, ShieldAlert, Award } from "lucide-react";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { driverColumns } from "./driver-columns";

function DriverDetailContent({ driver }: { driver: DriverProfile }) {
  return (
    <>
      <div className="px-6 pb-4 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-xl">
            {driver.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <h4 className="font-bold text-foreground text-lg">{driver.name}</h4>
            <p className="text-xs text-muted-foreground font-medium uppercase font-mono">{driver.id}</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Status</p>
            <p className={`text-sm font-bold uppercase ${
              driver.status === 'Active' ? 'text-brand-teal' :
              driver.status === 'On Break' ? 'text-amber-500' :
              'text-slate-600 dark:text-slate-400'
            }`}>{driver.status}</p>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
            <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Trip Score</p>
            <p className="text-sm font-bold text-brand-teal flex items-center gap-1">
              <Award className="w-4 h-4" /> {driver.avgTripScore}
            </p>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3">Performance Metrics</h5>
          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Trips Completed</p>
              <p className="text-sm font-bold font-mono text-foreground">{driver.tripsCompleted}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Customer Rating</p>
              <div className="flex items-center gap-1 text-sm font-bold text-brand-blue">
                {driver.rating.toFixed(1)} <Award className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>

        <div>
          <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3">Compliance & Safety</h5>
          <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border space-y-4">
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">License Status</p>
              <p className={`text-xs font-bold px-2 py-0.5 rounded uppercase ${
                driver.licenseStatus === "Valid" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                driver.licenseStatus === "Expiring Soon" ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400" :
                "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
              }`}>{driver.licenseStatus}</p>
            </div>
            <div className="flex justify-between items-center">
              <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Recent Incidents</p>
              <p className={`text-sm font-bold font-mono ${driver.recentIncidents > 0 ? "text-red-500" : "text-green-500"}`}>
                {driver.recentIncidents}
              </p>
            </div>
          </div>
        </div>
      </div>
    </>
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
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <UserCheck className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Active Shift</span>
            <span className="text-3xl font-bold text-foreground">{drivers.filter(d => d.status === "Active").length}</span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <ShieldAlert className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Compliance Flags</span>
            <span className="text-3xl font-bold text-foreground">{drivers.reduce((acc, curr) => acc + curr.recentIncidents, 0)}</span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Award className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Avg. Fleet Rating</span>
            <span className="text-3xl font-bold text-foreground">{(drivers.reduce((acc, curr) => acc + curr.rating, 0) / drivers.length).toFixed(1)}</span>
          </div>
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
