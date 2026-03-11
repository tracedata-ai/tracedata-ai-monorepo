"use client";

import { useState } from "react";
import Link from "next/link";
import { Search, UserCheck, ShieldAlert, Award, ExternalLink } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export default function DriversPage() {
  const { drivers: mockDrivers } = dashboardConfig;
  const [selectedDriverId, setSelectedDriverId] = useState<string | null>(null);

  const selectedDriver = mockDrivers.find(d => d.id === selectedDriverId) || null;

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
              <input 
                type="text" 
                placeholder="Search drivers..." 
                className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue"
              />
            </div>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
              Add Driver
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <UserCheck className="w-8 h-8 text-brand-teal absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Active Shift</span>
            <span className="text-3xl font-bold text-foreground">
              {mockDrivers.filter(d => d.status === "Active").length}
            </span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <ShieldAlert className="w-8 h-8 text-amber-500 absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Compliance Flags</span>
            <span className="text-3xl font-bold text-foreground">
              {mockDrivers.reduce((acc, curr) => acc + curr.recentIncidents, 0)}
            </span>
          </div>
          <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2 relative overflow-hidden">
            <Award className="w-8 h-8 text-brand-blue absolute right-6 top-6 opacity-20" />
            <span className="text-muted-foreground text-sm font-semibold uppercase tracking-wider">Avg. Fleet Rating</span>
            <span className="text-3xl font-bold text-foreground">
              {(mockDrivers.reduce((acc, curr) => acc + curr.rating, 0) / mockDrivers.length).toFixed(1)}
            </span>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-border overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-slate-800/50">
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Driver Profile</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trips</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Trip Score</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Rating</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-border">
              {mockDrivers.map((driver) => (
                <TableRow 
                  key={driver.id} 
                  onClick={() => setSelectedDriverId(driver.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedDriverId === driver.id ? "bg-brand-blue/5" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-sm">
                        {driver.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <div>
                        <p className="font-bold text-foreground">{driver.name}</p>
                        <p className="text-xs text-muted-foreground font-mono">{driver.id}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      driver.status === 'Active' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
                      driver.status === 'On Break' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                      'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                    }`}>
                      {driver.status}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="font-mono font-medium text-foreground">{driver.tripsCompleted}</span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span title="Average Trip Score (0-100)" className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-brand-teal/10 text-brand-teal border border-brand-teal/20">
                      <Award className="w-3 h-3 mr-1" />
                      {driver.avgTripScore}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-1.5" title="Customer Rating (1-5)">
                      <Award className="w-4 h-4 text-brand-blue" />
                      <span className="text-sm font-medium text-foreground">{driver.rating.toFixed(1)}</span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!selectedDriverId} onOpenChange={(open) => !open && setSelectedDriverId(null)}>
        <SheetContent className="w-full sm:max-w-md bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-xl">
          <SheetHeader className="sr-only">
            <SheetTitle>Driver Details</SheetTitle>
          </SheetHeader>
          
          {selectedDriver && (
            <div className="flex flex-col h-full mt-8">
              <div className="p-6 pt-2 border-b border-border">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-foreground tracking-tight">Driver Details</h3>
                  <Link 
                    href={`/dashboard/drivers/${selectedDriver.id}`}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-blue bg-brand-blue/10 hover:bg-brand-blue/20 px-3 py-1.5 rounded-md transition-colors"
                  >
                    Open Page <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-xl">
                    {selectedDriver.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground text-lg">{selectedDriver.name}</h4>
                    <p className="text-xs text-muted-foreground font-medium uppercase font-mono">{selectedDriver.id}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Status</p>
                    <p className={`text-sm font-bold uppercase ${
                      selectedDriver.status === 'Active' ? 'text-brand-teal' :
                      selectedDriver.status === 'On Break' ? 'text-amber-500' :
                      'text-slate-600 dark:text-slate-400'
                    }`}>
                      {selectedDriver.status}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1 tracking-wider">Trip Score</p>
                    <p className="text-sm font-bold text-brand-teal flex items-center gap-1">
                      <Award className="w-4 h-4" /> {selectedDriver.avgTripScore}
                    </p>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3">Performance metrics</h5>
                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border space-y-4">
                    <div className="flex justify-between items-center">
                      <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Trips Completed</p>
                      <p className="text-sm font-bold font-mono text-foreground">{selectedDriver.tripsCompleted}</p>
                    </div>
                    <div className="flex justify-between items-center">
                      <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Customer Rating</p>
                      <div className="flex items-center gap-1 text-sm font-bold text-brand-blue">
                        {selectedDriver.rating.toFixed(1)} <Award className="w-4 h-4" />
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
                        selectedDriver.licenseStatus === "Valid" ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400" :
                        "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                      }`}>
                        {selectedDriver.licenseStatus}
                      </p>
                    </div>
                    <div className="flex justify-between items-center">
                      <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Recent Incidents</p>
                      <p className={`text-sm font-bold font-mono ${
                        selectedDriver.recentIncidents > 0 ? "text-red-500" : "text-green-500"
                      }`}>
                        {selectedDriver.recentIncidents}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
