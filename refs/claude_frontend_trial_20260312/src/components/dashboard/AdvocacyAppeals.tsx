import { dashboardConfig } from "@/config/dashboard";

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
      
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead className="bg-muted/50 border-b border-border">
            <tr>
              <th className="px-6 py-3 text-[10px] font-bold text-muted-foreground uppercase">Driver / ID</th>
              <th className="px-6 py-3 text-[10px] font-bold text-muted-foreground uppercase">Contest Reason</th>
              <th className="px-6 py-3 text-[10px] font-bold text-muted-foreground uppercase">Priority</th>
              <th className="px-6 py-3 text-[10px] font-bold text-muted-foreground uppercase text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {appeals.map((appeal) => (
              <tr key={appeal.id} className="hover:bg-muted/30 transition-colors group">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img 
                      src={appeal.driverAvatarUrl} 
                      alt="" 
                      className="w-8 h-8 rounded-full border border-border" 
                    />
                    <div>
                      <div className="text-xs font-bold text-foreground">{appeal.driverName}</div>
                      <div className="text-[10px] text-muted-foreground">{appeal.driverId}</div>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-xs text-foreground/80 font-medium">{appeal.reason}</div>
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                    appeal.priority === 'Urgent' ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800' :
                    appeal.priority === 'Medium' ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500 border border-amber-200 dark:border-amber-800' :
                    'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700'
                  }`}>
                    {appeal.priority}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <button className="text-[11px] font-bold text-brand-blue hover:text-white hover:bg-brand-blue px-3 py-1.5 rounded-md border border-brand-blue/20 transition-all">
                    Review Case
                  </button>
                </td>
              </tr>
            ))}
            {appeals.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-sm text-muted-foreground">
                  No pending appeals. Fleet operating at consensus.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
