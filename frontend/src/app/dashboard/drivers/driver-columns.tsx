"use client"

import { ColumnDef } from "@tanstack/react-table"
import { Award } from "lucide-react"
import { DriverProfile } from "@/config/dashboard"

export const driverColumns: ColumnDef<DriverProfile>[] = [
  {
    accessorKey: "name",
    header: "Driver Profile",
    cell: ({ row }) => {
      const initials = row.original.name.split(' ').map(n => n[0]).join('')
      return (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-sm">
            {initials}
          </div>
          <div>
            <p className="font-bold text-foreground">{row.original.name}</p>
            <p className="text-xs text-muted-foreground font-mono">{row.original.id}</p>
          </div>
        </div>
      )
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.original.status
      const cls =
        status === 'Active' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
        status === 'On Break' ? 'bg-amber-500/10 text-amber-500 border border-amber-500/20' :
        'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
      return (
        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${cls}`}>
          {status}
        </span>
      )
    },
  },
  {
    accessorKey: "tripsCompleted",
    header: "Trips",
    cell: ({ row }) => (
      <span className="font-mono font-medium text-foreground">{row.original.tripsCompleted}</span>
    ),
  },
  {
    accessorKey: "avgTripScore",
    header: "Trip Score",
    cell: ({ row }) => (
      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold bg-brand-teal/10 text-brand-teal border border-brand-teal/20">
        <Award className="w-3 h-3 mr-1" />
        {row.original.avgTripScore}
      </span>
    ),
  },
  {
    accessorKey: "rating",
    header: "Rating",
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5">
        <Award className="w-4 h-4 text-brand-blue" />
        <span className="text-sm font-medium text-foreground">{row.original.rating.toFixed(1)}</span>
      </div>
    ),
  },
]
