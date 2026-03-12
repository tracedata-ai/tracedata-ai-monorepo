"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig, IssueRecord } from "@/config/dashboard";
import {
  ChevronRight,
  Brain,
  ArrowLeft,
  Calendar,
  Wrench,
  Clock,
  AlertTriangle,
  History,
  CheckCircle2,
  AlertCircle
} from "lucide-react";

import { GlassCard } from "@/components/shared/GlassCard";
import { MetricCard } from "@/components/shared/MetricCard";

export default function IssueDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const issueId = resolvedParams.id;
  
  const issue = dashboardConfig.issues.find((i) => i.id === issueId);
  
  if (!issue) {
    notFound();
  }

  const renderPriorityIcon = (priority: string) => {
    switch (priority) {
      case "Critical":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "High":
        return <AlertTriangle className="w-5 h-5 text-orange-500" />;
      case "Medium":
        return <Clock className="w-5 h-5 text-slate-400" />;
      case "Low":
        return <CheckCircle2 className="w-5 h-5 text-blue-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-slate-400" />;
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-xs font-bold text-muted-foreground uppercase tracking-widest">
          <Link href="/dashboard/issues" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-4 h-4" /> Issues Hub
          </Link>
          <ChevronRight className="w-4 h-4 mx-3 opacity-20" />
          <span className="text-foreground">{issue.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-black text-foreground tracking-tight">{issue.summary}</h1>
              <p className="text-muted-foreground font-medium mt-2 flex items-center gap-2">
                <span className="text-foreground font-bold">{issue.assetName}</span> (ID: {issue.vehicleId})
              </p>
            </div>
            
            {/* Status Button/Badge */}
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase border shadow-sm ${
                 issue.status === "Resolved"
                 ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800/50"
                 : "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
             }`}>
              {issue.status === "Resolved" && <div className="w-2 h-2 rounded-full bg-green-500"></div>}
              {issue.status === "Open" && <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>}
              {issue.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
             <div className="col-span-1 lg:col-span-1 space-y-6">
                <GlassCard className="p-6">
                   <h3 className="text-xs font-bold text-muted-foreground mb-5 uppercase tracking-wider">Properties</h3>
                   
                   <div className="space-y-5">
                      <div>
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Priority</p>
                         <div className="flex items-center gap-2 mt-1.5 font-bold text-foreground">
                            {renderPriorityIcon(issue.priority)} {issue.priority}
                         </div>
                      </div>
                      <div>
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Fault Type</p>
                         <p className="mt-1.5 font-bold text-foreground uppercase tracking-wider text-xs">{issue.type}</p>
                      </div>
                      <div>
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Reported Origin</p>
                         <p className="mt-1.5 font-medium text-foreground flex items-center gap-2">
                           <Calendar className="w-4 h-4 text-muted-foreground" />
                           {issue.reportedDate}
                         </p>
                      </div>
                   </div>
                </GlassCard>

                {issue.status === "Resolved" && (
                    <GlassCard className="p-6 bg-brand-teal/5 border-brand-teal/20">
                       <h3 className="text-xs font-bold text-brand-teal mb-5 uppercase tracking-wider flex items-center gap-2">
                         <CheckCircle2 className="w-4 h-4" /> Resolution Data
                       </h3>
                       <div className="space-y-5">
                          <div>
                            <p className="text-xs text-brand-teal/70 uppercase font-bold tracking-widest">Technician</p>
                            <p className="text-sm font-bold text-foreground mt-1.5">
                              {issue.technician}
                            </p>
                          </div>
                          <div>
                            <p className="text-xs text-brand-teal/70 uppercase font-bold tracking-widest">Action Taken</p>
                            <p className="text-sm text-slate-700 dark:text-slate-300 mt-1.5 leading-relaxed bg-white/50 dark:bg-slate-800/50 p-3 rounded border border-brand-teal/10">{issue.resolutionAction}</p>
                          </div>
                          <div>
                            <p className="text-xs text-brand-teal/70 uppercase font-bold tracking-widest">Resolved Date</p>
                            <p className="text-sm text-foreground font-bold mt-1.5 flex items-center gap-2 font-mono">
                               <Clock className="w-4 h-4 opacity-50" />
                               {issue.resolvedDate}
                            </p>
                          </div>
                       </div>
                    </GlassCard>
                )}
             </div>

             <div className="col-span-1 lg:col-span-3 space-y-6">
                {issue.agentReasoning && (
                    <GlassCard className="p-8 border-brand-blue/20 bg-brand-blue/5">
                      <h5 className="text-xs font-bold text-brand-blue uppercase tracking-wider mb-5 flex items-center gap-2">
                        <Brain className="w-5 h-5" /> AI Diagnostic Reasoning ({issue.agent})
                      </h5>
                      <div className="relative pl-6 border-l-4 border-brand-blue/30">
                        <p className="text-lg text-slate-800 dark:text-slate-200 leading-relaxed italic font-medium">
                          &quot;{issue.agentReasoning}&quot;
                        </p>
                      </div>
                      {issue.agentTags && (
                        <div className="mt-6 flex flex-wrap gap-2">
                          {issue.agentTags.map((tag) => (
                            <span
                              key={tag}
                              className="px-3 py-1 bg-white/50 text-brand-blue text-xs font-bold rounded-lg border border-brand-blue/10 shadow-sm uppercase tracking-tighter"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </GlassCard>
                )}

                <GlassCard className="p-8">
                  <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-8 flex items-center gap-2">
                    <History className="w-5 h-5 text-slate-400" /> Event Narrative Timeline
                  </h5>
                  <div className="relative pl-8 border-l-2 border-slate-100 dark:border-slate-800 space-y-10 ml-2">
                    {issue.timeline.map((event, idx) => (
                      <div key={idx} className="relative group">
                        <div className="absolute -left-[41px] top-1 w-4 h-4 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 group-hover:border-brand-blue transition-colors rounded-full z-10"></div>
                        <div>
                          <p className="text-base font-bold text-foreground group-hover:text-brand-blue transition-colors">
                            {event.title}
                          </p>
                          <p className="text-xs text-brand-blue font-bold mt-1 uppercase tracking-widest font-mono">
                            {event.timestamp}
                          </p>
                          <p className="text-sm text-muted-foreground mt-3 leading-relaxed max-w-2xl">
                            {event.description}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </GlassCard>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
