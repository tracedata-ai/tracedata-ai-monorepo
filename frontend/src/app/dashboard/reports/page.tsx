"use client";

import { FileText, Download, Calendar } from "lucide-react";

export default function ReportsPage() {
  const mockReports = [
    { id: "REP-992", name: "Weekly Fleet Efficiency Summary", date: "Oct 24, 2026", size: "2.4 MB", type: "PDF" },
    { id: "REP-991", name: "Driver Burnout Heatmap Export", date: "Oct 23, 2026", size: "1.1 MB", type: "CSV" },
    { id: "REP-990", name: "Agent Decision Trace Log (AG-04)", date: "Oct 22, 2026", size: "15.8 MB", type: "JSON" },
  ];

  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="reports-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Analytics & Reports</h2>
          <p className="text-muted-foreground text-sm">Generate and download historical fleet data.</p>
        </div>
        <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm flex items-center gap-2">
          <FileText className="w-4 h-4" />
          Generate New Report
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold">Total Reports Generated</span>
          <span className="text-3xl font-bold text-foreground">142</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold">Storage Used</span>
          <span className="text-3xl font-bold text-foreground">8.4 GB</span>
        </div>
        <div className="bg-card p-6 rounded-xl border border-border shadow-sm flex flex-col gap-2">
          <span className="text-muted-foreground text-sm font-semibold">Scheduled Reports</span>
          <span className="text-3xl font-bold text-foreground">3 <span className="text-sm font-medium text-muted-foreground">/ week</span></span>
        </div>
      </div>

      <h3 className="text-lg font-bold text-foreground mt-8 mb-4">Recent Downloads</h3>
      <div className="bg-card rounded-xl border border-border overflow-hidden shadow-sm">
        <div className="divide-y divide-border">
          {mockReports.map((report) => (
            <div key={report.id} className="p-4 hover:bg-muted/30 transition-colors flex items-center justify-between group cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-muted rounded-lg text-muted-foreground group-hover:bg-brand-blue/10 group-hover:text-brand-blue transition-colors">
                  <FileText className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-foreground group-hover:text-brand-blue transition-colors">{report.name}</h4>
                  <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {report.date}</span>
                    <span>•</span>
                    <span className="font-mono">{report.size}</span>
                    <span>•</span>
                    <span className="uppercase font-bold">{report.type}</span>
                  </div>
                </div>
              </div>
              <button className="p-2 text-muted-foreground hover:text-brand-blue hover:bg-brand-blue/10 rounded-lg transition-colors focus:outline-none">
                <Download className="w-5 h-5" />
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
