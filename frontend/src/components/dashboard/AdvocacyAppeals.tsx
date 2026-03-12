import { dashboardConfig, AppealContest } from "@/config/dashboard";
import { DataTable } from "@/components/shared/data-table";
import { ColumnDef } from "@tanstack/react-table";

const columns: ColumnDef<AppealContest>[] = [
  {
    accessorKey: "driverName",
    header: "Driver / ID",
    cell: ({ row }) => (
      <div className="flex items-center gap-3 text-left">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img 
          src={row.original.driverAvatarUrl} 
          alt="" 
          className="w-8 h-8 rounded-full border border-border" 
        />
        <div>
          <div className="text-xs font-bold text-foreground">{row.original.driverName}</div>
          <div className="text-[10px] text-muted-foreground">{row.original.driverId}</div>
        </div>
      </div>
    ),
  },
  {
    accessorKey: "reason",
    header: "Contest Reason",
    cell: ({ row }) => (
      <div className="text-xs text-foreground/80 font-medium text-left">{row.original.reason}</div>
    ),
  },
  {
    accessorKey: "priority",
    header: "Priority",
    cell: ({ row }) => (
      <div className="text-left">
        <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
          row.original.priority === 'Urgent' ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800' :
          row.original.priority === 'Medium' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500 border border-amber-200 dark:border-amber-800' :
          'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
        }`}>
          {row.original.priority}
        </span>
      </div>
    ),
  },
  {
    id: "actions",
    header: () => <div className="text-right">Action</div>,
    cell: () => (
      <div className="text-right">
        <button className="text-[11px] font-bold text-brand-blue hover:text-white hover:bg-brand-blue px-3 py-1.5 rounded-md border border-brand-blue/20 transition-all">
          Review Case
        </button>
      </div>
    ),
  },
];

export function AdvocacyAppeals() {
  const { appeals } = dashboardConfig;

  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm" data-purpose="advocacy-appeals">
      <div className="p-6 border-b border-border flex justify-between items-center">
        <div>
          <h3 className="text-sm font-bold text-foreground">Advocacy & Appeals</h3>
          <p className="text-xs text-muted-foreground">Pending driver contests requiring manual oversight</p>
        </div>
        <button className="text-[10px] uppercase font-bold text-brand-blue hover:text-brand-blue/80 px-3 py-1 bg-brand-blue/10 rounded-md transition-colors">
          View All
        </button>
      </div>
      
      <div className="p-0">
        <DataTable 
          columns={columns} 
          data={appeals} 
        />
      </div>
    </div>
  );
}
