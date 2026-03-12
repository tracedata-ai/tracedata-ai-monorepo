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
          <div className="w-10 h-10 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue font-black text-sm border border-brand-blue/10 shadow-sm">
            {initials}
          </div>
          <div>
            <p className="text-sm font-bold text-foreground">{row.original.name}</p>
            <p className="text-[10px] text-muted-foreground font-mono uppercase tracking-tighter">{row.original.id}</p>
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
        status === 'Active' ? 'bg-brand-teal/5 text-brand-teal border-brand-teal/10' :
        status === 'On Break' ? 'bg-amber-500/5 text-amber-500 border-amber-500/10' :
        'bg-slate-50 text-slate-500 border-slate-100'
      return (
        <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border ${cls}`}>
          {status}
        </span>
      )
    },
  },
  {
    accessorKey: "tripsCompleted",
    header: "Trips",
    cell: ({ row }) => (
      <span className="font-mono text-[10px] font-bold text-slate-600 uppercase tracking-tighter">{row.original.tripsCompleted}</span>
    ),
  },
  {
    accessorKey: "avgTripScore",
    header: "Trip Score",
    cell: ({ row }) => (
      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold bg-brand-teal/5 text-brand-teal border border-brand-teal/10 tracking-wider uppercase">
        <Award className="w-3.5 h-3.5 mr-1" />
        {row.original.avgTripScore}
      </span>
    ),
  },
  {
    accessorKey: "rating",
    header: "Rating",
    cell: ({ row }) => (
      <div className="flex items-center gap-1.5">
        <Award className="w-3.5 h-3.5 text-brand-blue" />
        <span className="text-xs font-bold text-foreground font-mono">{row.original.rating.toFixed(1)}</span>
      </div>
    ),
  },
]
