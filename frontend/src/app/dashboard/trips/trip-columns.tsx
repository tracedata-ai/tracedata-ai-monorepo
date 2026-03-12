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
    case "In Progress": return "bg-brand-blue/5 text-brand-blue border-brand-blue/10"
    case "Completed": return "bg-brand-teal/5 text-brand-teal border-brand-teal/10"
    case "Scheduled": return "bg-slate-50 text-slate-500 border-slate-100"
    case "Cancelled": return "bg-rose-50 text-rose-500 border-rose-100"
    default: return ""
  }
}

export const tripColumns: ColumnDef<TripRecord>[] = [
  {
    accessorKey: "id",
    header: "Trip ID",
    cell: ({ row }) => (
      <span className="font-mono text-[10px] font-bold text-slate-600 uppercase tracking-tighter">{row.original.id}</span>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${getTripStatusClass(row.original.status)}`}>
        {row.original.status}
      </span>
    ),
  },
  {
    accessorKey: "routeId",
    header: "Route",
    cell: ({ row }) => (
      <div className="flex items-center gap-2 text-[10px] font-bold text-brand-blue uppercase tracking-widest bg-brand-blue/5 px-2 py-1 rounded-md border border-brand-blue/10 w-fit">
        <Route className="w-3.5 h-3.5" />
        <span>{row.original.routeId}</span>
      </div>
    ),
  },
  {
    accessorKey: "driverId",
    header: "Assignment",
    cell: ({ row }) => (
      <div className="flex flex-col">
        <span className="text-sm font-bold text-foreground">{row.original.driverId}</span>
        <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-tighter">{row.original.vehicleId}</span>
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
          <div className="flex justify-between items-center text-[10px] font-mono font-bold tracking-tighter">
            <span className="text-brand-blue">{(trip.currentDistanceKm ?? 0).toFixed(1)}km</span>
            <span className="text-slate-400">{trip.distanceKm.toFixed(1)}km</span>
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
