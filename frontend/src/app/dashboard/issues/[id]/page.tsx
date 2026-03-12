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
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";

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
      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={4} className="py-6">
          <div className="col-span-1 lg:col-span-4 flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-4">
            <div>
              <h1 className="text-2xl font-black text-slate-900 tracking-tight">{issue.summary}</h1>
              <p className="text-muted-foreground font-bold mt-1.5 flex items-center gap-2 text-sm uppercase tracking-tight">
                <span className="text-brand-blue">{issue.assetName}</span>
                <span className="w-1 h-1 rounded-full bg-slate-300"></span>
                <span className="font-mono text-[10px]">{issue.vehicleId}</span>
              </p>
            </div>
            
            <div className={`px-3 py-1.5 flex items-center gap-2 rounded-md text-[10px] font-bold uppercase border shadow-sm ${
                 issue.status === "Resolved"
                 ? "bg-emerald-50 text-emerald-600 border-emerald-100"
                 : "bg-amber-50 text-amber-600 border-amber-100"
             }`}>
              {issue.status === "Resolved" && <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"></div>}
              {issue.status === "Open" && <div className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse shadow-sm shadow-amber-500/50"></div>}
              {issue.status}
            </div>
          </div>
          
          <div className="col-span-1 lg:col-span-1 space-y-6">
            <InfoCard
              title="Properties"
              items={[
                { 
                  label: "Priority", 
                  value: (
                    <div className="flex items-center gap-2">
                      {renderPriorityIcon(issue.priority)} {issue.priority}
                    </div>
                  ),
                  className: "col-span-2"
                },
                { label: "Fault Type", value: issue.type, className: "col-span-2" },
                { 
                  label: "Reported Origin", 
                  value: issue.reportedDate, 
                  icon: Calendar, 
                  className: "col-span-2" 
                }
              ]}
              columns={1}
              className="p-3"
            />

            {issue.status === "Resolved" && (
              <InfoCard
                title="Resolution Data"
                icon={CheckCircle2}
                variant="brand"
                items={[
                  { label: "Technician", value: issue.technician, className: "col-span-2" },
                  { label: "Action Taken", value: issue.resolutionAction, className: "col-span-2" },
                  { label: "Resolved Date", value: issue.resolvedDate, icon: Clock, className: "col-span-2" }
                ]}
                columns={1}
              />
            )}
          </div>

          <div className="col-span-1 lg:col-span-3 space-y-6">
            {issue.agentReasoning && (
              <FeatureCard
                title={`AI Diagnostic Reasoning (${issue.agent})`}
                icon={Brain}
                variant="brand"
                isNarrative
                className="p-4"
              >
                {issue.agentReasoning}
                {issue.agentTags && (
                  <div className="mt-4 flex flex-wrap gap-1.5">
                    {issue.agentTags.map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-white text-brand-blue text-[10px] font-bold rounded border border-brand-blue/10 shadow-sm uppercase tracking-tighter">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </FeatureCard>
            )}

            <FeatureCard
              title="Event Narrative Timeline"
              icon={History}
              className="p-4"
            >
              <div className="relative pl-6 border-l-2 border-slate-100 dark:border-slate-800 space-y-6 ml-1">
                {issue.timeline.map((event, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-[31.5px] top-1 w-3 h-3 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 group-hover:border-brand-blue transition-colors rounded-full z-10"></div>
                    <div>
                      <p className="text-sm font-bold text-slate-900 group-hover:text-brand-blue transition-colors">
                        {event.title}
                      </p>
                      <p className="text-[10px] text-brand-blue font-bold mt-0.5 uppercase tracking-widest font-mono">
                        {event.timestamp}
                      </p>
                      <p className="text-xs text-slate-500 mt-2 leading-relaxed max-w-2xl">
                        {event.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </FeatureCard>
          </div>
        </DashboardSection>
      </main>
    </div>
  );
}
