"use client";

import { Truck, MapPin, Navigation, SignalHigh } from "lucide-react";

import { dashboardConfig } from "@/config/dashboard";

export default function FleetPage() {
  const { vehicles } = dashboardConfig;

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="fleet-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Fleet Telemetry</h2>
          <p className="text-muted-foreground text-sm">Real-time vehicle tracking and status monitoring.</p>
        </div>
        <div className="flex gap-3">
          <button className="bg-background border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:bg-muted transition-colors shadow-sm focus:outline-none">
            Export Data
          </button>
          <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm focus:outline-none">
            Register Vehicle
          </button>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Vehicle ID</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Plate & Model</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Assigned Driver</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Location</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Operating Hrs</th>
                <th className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Telemetry Signal</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {vehicles.map((vehicle) => (
                <tr key={vehicle.id} className="hover:bg-muted/30 transition-colors group cursor-pointer">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-brand-blue/10 text-brand-blue rounded-lg">
                        <Truck className="w-4 h-4" />
                      </div>
                      <span className="font-mono font-bold text-foreground">{vehicle.id}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-bold text-foreground text-sm">{vehicle.plateNumber}</span>
                      <span className="text-xs text-muted-foreground">{vehicle.model}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-medium text-foreground">{vehicle.driver}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold ${
                      vehicle.status === 'In Transit' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
                      vehicle.status === 'Charging' ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20' :
                      vehicle.status === 'Maintenance' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
                      'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                    }`}>
                      {vehicle.status === 'In Transit' && <Navigation className="w-3 h-3" />}
                      {vehicle.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm">
                      <MapPin className="w-4 h-4" />
                      {vehicle.location}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="font-mono font-medium text-brand-teal">{vehicle.operatingHours.toLocaleString()}h</span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <SignalHigh className={`w-4 h-4 ${
                        vehicle.signal === 'Strong' ? 'text-brand-teal' :
                        vehicle.signal === 'Medium' ? 'text-amber-500' :
                        'text-red-500'
                      }`} />
                      <span className="text-sm font-medium text-foreground">{vehicle.signal}</span>
                    </div>
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
