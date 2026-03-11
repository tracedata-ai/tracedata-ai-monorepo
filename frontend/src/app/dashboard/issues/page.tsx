"use client";

import { AlertTriangle, AlertCircle, Info, CheckCircle2 } from "lucide-react";

export default function IssuesPage() {
  const mockIssues = [
    { id: "ISS-001", type: "System Alert", severity: "Critical", message: "Telemetry loss on Vehicle VEH-9923 for > 5 minutes.", time: "10 mins ago", status: "Open" },
    { id: "ISS-002", type: "Driver Contest", severity: "High", message: "Elena Petrov contesting automated break schedule penalty.", time: "1 hr ago", status: "Under Review" },
    { id: "ISS-003", type: "Agent Warning", severity: "Medium", message: "Behavior Agent (AG-04) detecting anomalous clustering in Sector 7G.", time: "2 hrs ago", status: "Open" },
    { id: "ISS-004", type: "System Alert", severity: "Low", message: "Daily database optimization routine completed successfully.", time: "5 hrs ago", status: "Resolved" },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="issues-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Issue Resolution Center</h2>
          <p className="text-muted-foreground text-sm">Manage system alerts, agent warnings, and driver appeals.</p>
        </div>
        <div className="flex gap-2 bg-muted p-1 rounded-lg border border-border">
          <button className="px-4 py-1.5 text-sm font-bold bg-background shadow-sm rounded-md text-foreground">All Issues</button>
          <button className="px-4 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Pending (3)</button>
          <button className="px-4 py-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Resolved</button>
        </div>
      </div>

      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
          <h3 className="font-bold text-sm text-foreground">Action Required</h3>
          <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 font-bold px-2 py-1 rounded-md">3 Open</span>
        </div>
        <div className="divide-y divide-border">
          {mockIssues.map((issue) => (
            <div key={issue.id} className="p-4 hover:bg-muted/10 transition-colors flex items-start gap-4">
              <div className="mt-1">
                {issue.severity === 'Critical' && <AlertCircle className="w-5 h-5 text-red-500" />}
                {issue.severity === 'High' && <AlertTriangle className="w-5 h-5 text-amber-500" />}
                {issue.severity === 'Medium' && <AlertTriangle className="w-5 h-5 text-amber-400" />}
                {issue.severity === 'Low' && <CheckCircle2 className="w-5 h-5 text-brand-teal" />}
              </div>
              <div className="flex-1 space-y-1">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-sm text-foreground">{issue.message}</h4>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">{issue.time}</span>
                </div>
                <div className="flex items-center gap-3 mt-2">
                  <span className="text-xs font-mono text-muted-foreground">{issue.id}</span>
                  <span className="text-xs font-medium text-muted-foreground">•</span>
                  <span className="text-xs font-medium text-muted-foreground">{issue.type}</span>
                  <span className="text-xs font-medium text-muted-foreground">•</span>
                  <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                    issue.status === 'Resolved' ? 'bg-brand-teal/10 text-brand-teal border border-brand-teal/20' :
                    'bg-muted border border-border text-foreground'
                  }`}>
                    {issue.status}
                  </span>
                </div>
              </div>
              <div>
                <button className="text-brand-blue text-sm font-bold hover:underline">View Details</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
