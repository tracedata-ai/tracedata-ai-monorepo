"use client"

import { ColumnDef } from "@tanstack/react-table"
import { ArrowRight } from "lucide-react"
import { RouteRecord } from "@/config/dashboard"

function formatMinsToHours(mins: number): string {
  const hours = Math.floor(mins / 60)
  const remainingMins = mins % 60
  return hours > 0 
    ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
    : `${remainingMins}m`
}

export const routeColumns: ColumnDef<RouteRecord>[] = [
  {
    accessorKey: "id",
    header: "Route ID",
    cell: ({ row }) => (
      <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-brand-blue/10 text-brand-blue border border-brand-blue/20">
        {row.original.id}
      </span>
    ),
  },
  {
    accessorKey: "name",
    header: "Path Details",
    cell: ({ row }) => (
      <div className="flex flex-col gap-1">
        <span className="font-bold text-foreground text-sm">{row.original.name}</span>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="truncate max-w-[120px]">{row.original.origin}</span>
          <ArrowRight className="w-3 h-3 text-brand-teal shrink-0" />
          <span className="truncate max-w-[120px]">{row.original.destination}</span>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "historicalAvgMins",
    header: "Hist. Avg Time",
    cell: ({ row }) => (
      <span className="font-medium text-foreground">{formatMinsToHours(row.original.historicalAvgMins)}</span>
    ),
  },
  {
    accessorKey: "standardDistanceKm",
    header: "Std Distance",
    cell: ({ row }) => (
      <span className="font-medium text-foreground">{row.original.standardDistanceKm.toFixed(1)} km</span>
    ),
  },
  {
    accessorKey: "totalTripsCompleted",
    header: "Trips Run",
    cell: ({ row }) => (
      <span className="font-mono font-medium text-brand-teal">{row.original.totalTripsCompleted.toLocaleString()}</span>
    ),
  },
]

export { formatMinsToHours as formatRouteMins }
