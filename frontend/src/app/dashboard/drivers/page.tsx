"use client";

import { Users, Search, UserCheck, ShieldAlert, Award } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";

export default function DriversPage() {
  const { drivers: mockDrivers } = dashboardConfig;

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="drivers-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Driver Operations</h2>
          <p className="text-muted-foreground text-sm">Manage fleet drivers, view shift compliance, and monitor performance.</p>
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search driver by ID or Name..." 
              className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue"
            />
          </div>
          <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm focus:outline-none">
            Add Driver
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <UserCheck className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Active Shift</span>
          <span className="text-3xl font-bold text-foreground">3</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <ShieldAlert className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Compliance Flags</span>
          <span className="text-3xl font-bold text-foreground">1</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
          <Award className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
          <span className="text-muted-foreground text-sm font-semibold">Avg. Fleet Rating</span>
          <span className="text-3xl font-bold text-foreground">4.8</span>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Driver Profile</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trips</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trip Score</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Rating</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockDrivers.map((driver) => (
                <tr key={driver.id} className="hover:bg-muted/30 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-sm">
                        {driver.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="font-bold text-foreground">{driver.name}</p>
                        <p className="text-xs text-muted-foreground font-mono">{driver.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold ${
                      driver.status === 'Active' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
                      driver.status === 'On Break' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                      'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                    }`}>
                      {driver.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono font-medium text-foreground">{driver.tripsCompleted}</span>
                  </td>
                  <td className="px-6 py-4">
                    <span title="Average Trip Score (0-100)" className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-brand-teal/10 text-brand-teal border border-brand-teal/20">
                      <Award className="w-3 h-3 mr-1" />
                      {driver.avgTripScore}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-1.5" title="Customer Rating (1-5)">
                      <Award className="w-4 h-4 text-brand-blue" />
                      <span className="text-sm font-medium text-foreground">{driver.rating.toFixed(1)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-sm font-bold text-brand-blue hover:underline">View File</button>
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
