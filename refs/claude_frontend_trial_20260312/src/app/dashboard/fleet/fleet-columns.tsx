"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Truck, MapPin, Navigation, SignalHigh, Wrench, BatteryCharging, PowerOff } from "lucide-react"
import { VehicleProfile } from "@/config/dashboard"

export const fleetColumns: ColumnDef<VehicleProfile>[] = [
  {
    accessorKey: "id",
    header: "Vehicle ID",
    cell: ({ row }) => (
      <div className="flex items-center gap-3">
        <div className="p-2 bg-brand-blue/5 text-brand-blue rounded-xl border border-brand-blue/10 shadow-sm">
          <Truck className="w-4 h-4" />
        </div>
        <span className="font-mono text-[10px] font-bold text-slate-600 uppercase tracking-tighter">{row.original.id}</span>
      </div>
    ),
  },
  {
    accessorKey: "plateNumber",
    header: "Plate & Model",
    cell: ({ row }) => (
      <div className="flex flex-col">
        <span className="text-sm font-bold text-foreground tracking-tight">{row.original.plateNumber}</span>
        <span className="text-[10px] text-muted-foreground font-bold uppercase tracking-wider">{row.original.model}</span>
      </div>
    ),
  },
  {
    accessorKey: "driver",
    header: "Assigned Driver",
    cell: ({ row }) => (
      <div className="text-sm font-bold text-foreground">{row.original.driver || '--'}</div>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      const cls =
        status === 'In Transit' ? 'bg-brand-teal/10 text-brand-teal border-brand-teal/20' :
        status === 'Charging' ? 'bg-blue-500/10 text-blue-500 border-blue-500/20' :
        status === 'Maintenance' ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' :
        'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border-slate-200 dark:border-slate-700'
      const icon =
        status === 'In Transit' ? <Navigation className="w-3 h-3" /> :
        status === 'Charging' ? <BatteryCharging className="w-3 h-3" /> :
        status === 'Maintenance' ? <Wrench className="w-3 h-3" /> :
        <PowerOff className="w-3 h-3" />
      return (
        <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${cls}`}>
          {icon} {status}
        </span>
      )
    },
  },
  {
    accessorKey: "location",
    header: "Location",
    cell: ({ row }) => (
      <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold uppercase tracking-tight">
        <MapPin className="w-3.5 h-3.5 shrink-0 text-brand-blue" />
        <span className="truncate max-w-[150px] block">{row.original.location || '--'}</span>
      </div>
    ),
  },
  {
    accessorKey: "operatingHours",
    header: "Operating Hrs",
    cell: ({ row }) => (
      <span className="font-mono text-[10px] font-bold text-slate-600 uppercase tracking-tighter">{row.original.operatingHours.toLocaleString()}h</span>
    ),
  },
  {
    accessorKey: "signal",
    header: "Telemetry Signal",
    cell: ({ row }) => {
      const signal = row.original.signal
      const cls = signal === 'Strong' ? 'text-brand-teal' : signal === 'Medium' ? 'text-amber-500' : 'text-red-500'
      return (
        <div className="flex items-center gap-2">
          <SignalHigh className={`w-3.5 h-3.5 ${cls}`} />
          <span className="text-[10px] font-bold text-foreground uppercase tracking-wider">{signal}</span>
        </div>
      )
    },
  },
]
