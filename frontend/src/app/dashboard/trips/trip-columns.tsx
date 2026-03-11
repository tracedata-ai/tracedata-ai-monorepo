"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Route } from "lucide-react"
import { TripRecord } from "@/config/dashboard"

function formatMinsToHours(mins: number): string {
  const hours = Math.floor(mins / 60)
  const remainingMins = mins % 60
  return hours > 0 
    ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
    : `${remainingMins}m`
}

function getTripStatusClass(status: string): string {
  switch (status) {
    case "In Progress": return "bg-brand-blue/10 text-brand-blue border border-brand-blue/20"
    case "Completed": return "bg-brand-teal/10 text-brand-teal border border-brand-teal/20"
    case "Scheduled": return "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700"
    case "Cancelled": return "bg-red-500/10 text-red-500 border border-red-500/20"
    default: return ""
  }
}

export const tripColumns: ColumnDef<TripRecord>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
    cell: ({ row }) => (
      <span className="font-mono text-sm font-bold text-foreground">{row.original.id}</span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider ${getTripStatusClass(row.original.status)}`}>
        {row.original.status}
      </span>
    ),
  },
  {
    accessorKey: "routeId",
    header: "Route",
    cell: ({ row }) => (
      <div className="flex items-center gap-2 text-sm font-bold text-brand-blue/80">
        <Route className="w-4 h-4" />
        <span>{row.original.routeId}</span>
      </div>
    ),
  },
  {
    accessorKey: "driverId",
    header: "Assignment",
    cell: ({ row }) => (
      <div className="flex flex-col gap-1">
        <span className="text-sm font-bold text-foreground">{row.original.driverId}</span>
        <span className="text-xs text-muted-foreground font-mono">{row.original.vehicleId}</span>
      </div>
    ),
  },
  {
    accessorKey: "distanceKm",
    header: "Distance",
    cell: ({ row }) => {
      const trip = row.original
      const pct = Math.min(100, ((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)
      return (
        <div className="flex flex-col gap-1.5 w-full min-w-[160px]">
          <div className="flex justify-between items-center text-xs font-mono font-bold">
            <span className="text-foreground">{(trip.currentDistanceKm ?? 0).toFixed(1)}km</span>
            <span className="text-muted-foreground">{trip.distanceKm.toFixed(1)}km</span>
          </div>
          <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${trip.status === 'Completed' ? 'bg-brand-teal' : 'bg-brand-blue'}`}
              style={{ width: `${pct}%` }}
            />
          </div>
        </div>
      )
    },
  },
]

export { formatMinsToHours as formatTripMins }
