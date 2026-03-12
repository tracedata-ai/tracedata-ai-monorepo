"use client"

import { ColumnDef } from "@tanstack/react-table"
import { AlertCircle, Clock, CheckCircle2, XCircle, Brain } from "lucide-react"
import { IssueRecord } from "@/config/dashboard"
import { cn } from "@/lib/utils"

const renderPriorityIcon = (priority: string) => {
  switch (priority) {
    case "Critical":
      return <AlertCircle className="w-4 h-4 text-red-500" />
    case "High":
      return <AlertCircle className="w-4 h-4 text-orange-500" />
    case "Medium":
      return <Clock className="w-4 h-4 text-slate-400" />
    case "Low":
      return <CheckCircle2 className="w-4 h-4 text-blue-500" />
    default:
      return null
  }
}

const getStatusBadgeClass = (status: string) => {
  switch (status) {
    case "Resolved":
      return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/50"
    case "Open":
      return "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
    case "Overdue":
      return "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800/50"
    case "Closed":
      return "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
    default:
      return "bg-slate-100 text-slate-600"
  }
}

export const issueColumns: ColumnDef<IssueRecord>[] = [
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        {renderPriorityIcon(row.original.priority)}
        <span className={cn(
          "text-[10px] font-bold uppercase tracking-wider",
          row.original.priority === 'Critical' ? 'text-rose-500' :
          row.original.priority === 'High' ? 'text-amber-500' :
          'text-slate-500'
        )}>{row.original.priority}</span>
      </div>
    ),
  },
  {
    accessorKey: "assetName",
    header: "Asset",
    cell: ({ row }) => (
      <div className="flex flex-col">
        <span className="text-sm font-bold text-foreground">{row.original.assetName}</span>
        <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-tighter">{row.original.vehicleId}</span>
      </div>
    ),
  },
  {
    accessorKey: "type",
    header: "Fault Type",
    cell: ({ row }) => (
      <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{row.original.type}</span>
    ),
  },
  {
    accessorKey: "summary",
    header: "Issue Summary",
    cell: ({ row }) => (
      <div className="max-w-[200px]">
        <span className="text-sm font-bold text-foreground line-clamp-1">{row.original.summary}</span>
        <span className="text-[10px] text-muted-foreground font-mono uppercase tracking-tighter">{row.original.id}</span>
      </div>
    ),
  },
  {
    accessorKey: "agent",
    header: "AI Agent",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <div className={`p-1 rounded-md ${row.original.agent.includes('Safety') ? 'bg-red-500/10 text-red-500' : 'bg-brand-blue/10 text-brand-blue'}`}>
          <Brain className="w-3.5 h-3.5" />
        </div>
        <span className="text-xs font-bold text-foreground">{row.original.agent}</span>
      </div>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <span className={cn(
        "inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider border",
        getStatusBadgeClass(row.original.status)
      )}>
        {row.original.status}
      </span>
    ),
  },
  {
    accessorKey: "reportedDate",
    header: "Reported",
    cell: ({ row }) => (
      <span className="text-xs text-muted-foreground font-medium">{row.original.reportedDate}</span>
    ),
  },
]
