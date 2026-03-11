"use client";

import { useState } from "react";
import Link from "next/link";
import { Truck, MapPin, Navigation, SignalHigh, ExternalLink, Activity, Wrench, BatteryCharging, PowerOff } from "lucide-react";
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

export default function FleetPage() {
  const { vehicles } = dashboardConfig;
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);

  const selectedVehicle = vehicles.find((v) => v.id === selectedVehicleId) || null;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'In Transit': return 'bg-brand-teal/10 text-brand-teal border-brand-teal/20';
      case 'Charging': return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
      case 'Maintenance': return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
      case 'Idle': return 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700';
      default: return "";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'In Transit': return <Navigation className="w-3 h-3" />;
      case 'Charging': return <BatteryCharging className="w-3 h-3" />;
      case 'Maintenance': return <Wrench className="w-3 h-3" />;
      case 'Idle': return <PowerOff className="w-3 h-3" />;
      default: return null;
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden" data-purpose="fleet-page">
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">Fleet Telemetry</h2>
            <p className="text-muted-foreground mt-1 text-sm">Real-time vehicle tracking and status monitoring.</p>
          </div>
          <div className="flex gap-3">
            <button className="bg-background border border-border text-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:bg-muted transition-colors shadow-sm focus:outline-none">
              Export Data
            </button>
            <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
              Register Vehicle
            </button>
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-border overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-slate-800/50">
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Vehicle ID</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Plate & Model</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Assigned Driver</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Status</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Location</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Operating Hrs</TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">Telemetry Signal</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-border">
              {vehicles.map((vehicle) => (
                <TableRow 
                  key={vehicle.id} 
                  onClick={() => setSelectedVehicleId(vehicle.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedVehicleId === vehicle.id ? "bg-brand-blue/5" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-brand-blue/10 text-brand-blue rounded-lg">
                        <Truck className="w-4 h-4" />
                      </div>
                      <span className="font-mono font-bold text-foreground">{vehicle.id}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-bold text-foreground text-sm">{vehicle.plateNumber}</span>
                      <span className="text-xs text-muted-foreground">{vehicle.model}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="font-medium text-foreground">{vehicle.driver || '--'}</div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border ${getStatusColor(vehicle.status)}`}>
                      {getStatusIcon(vehicle.status)}
                      {vehicle.status}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm font-medium">
                      <MapPin className="w-4 h-4 shrink-0" />
                      <span className="truncate max-w-[150px] block">{vehicle.location || '--'}</span>
                    </div>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="font-mono font-bold text-foreground">{vehicle.operatingHours.toLocaleString()}h</span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <SignalHigh className={`w-4 h-4 ${
                        vehicle.signal === 'Strong' ? 'text-brand-teal' :
                        vehicle.signal === 'Medium' ? 'text-amber-500' :
                        'text-red-500'
                      }`} />
                      <span className="text-sm font-bold text-foreground">{vehicle.signal}</span>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!selectedVehicleId} onOpenChange={(open) => !open && setSelectedVehicleId(null)}>
        <SheetContent className="w-full sm:max-w-md bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-xl">
          <SheetHeader className="sr-only">
            <SheetTitle>Vehicle Details</SheetTitle>
          </SheetHeader>
          
          {selectedVehicle && (
            <div className="flex flex-col h-full mt-8">
              <div className="p-6 pt-2 border-b border-border">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-foreground tracking-tight">Vehicle Details</h3>
                  <Link 
                    href={`/dashboard/fleet/${selectedVehicle.id}`}
                    className="flex items-center gap-1.5 text-xs font-bold text-brand-blue bg-brand-blue/10 hover:bg-brand-blue/20 px-3 py-1.5 rounded-md transition-colors"
                  >
                    Open Page <ExternalLink className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
                    <Truck className="w-6 h-6" />
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground text-lg leading-tight font-mono">{selectedVehicle.id}</h4>
                    <p className="text-xs font-bold text-muted-foreground mt-1 tracking-widest uppercase">{selectedVehicle.plateNumber}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className={`p-3 rounded-lg border flex items-center gap-2 font-bold text-sm ${getStatusColor(selectedVehicle.status)}`}>
                    {getStatusIcon(selectedVehicle.status)} {selectedVehicle.status}
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg border border-border flex flex-col justify-center">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-0.5 tracking-wider">Signal</p>
                    <div className="flex items-center gap-1.5">
                      <SignalHigh className={`w-3.5 h-3.5 ${
                        selectedVehicle.signal === 'Strong' ? 'text-brand-teal' :
                        selectedVehicle.signal === 'Medium' ? 'text-amber-500' :
                        'text-red-500'
                      }`} />
                      <span className="text-xs font-bold text-foreground">{selectedVehicle.signal}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                <div>
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-brand-blue" /> Diagnostics & Stats
                  </h5>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Model</p>
                      <p className="text-sm font-bold text-foreground mt-1 truncate">
                        {selectedVehicle.model}
                      </p>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border">
                      <p className="text-[10px] text-slate-500 uppercase font-bold tracking-wider">Total Op Hours</p>
                      <p className="text-sm font-bold text-foreground font-mono mt-1">
                        {selectedVehicle.operatingHours.toLocaleString()}h
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                   <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-3 flex items-center gap-2">
                     <MapPin className="w-4 h-4 text-brand-teal" /> Context
                   </h5>
                   <div className="space-y-3">
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-border flex justify-between items-center">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-wider">Driver</p>
                         {selectedVehicle.driver ? (
                           <Link href={`/dashboard/drivers/${selectedVehicle.driver}`} className="text-sm font-bold text-brand-blue hover:underline">
                             {selectedVehicle.driver}
                           </Link>
                         ) : (
                           <p className="text-sm font-medium text-muted-foreground">Unassigned</p>
                         )}
                      </div>
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-lg border border-border">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-wider mb-1">Last Loc</p>
                         <p className="text-sm font-bold text-foreground">{selectedVehicle.location || 'Unknown'}</p>
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
