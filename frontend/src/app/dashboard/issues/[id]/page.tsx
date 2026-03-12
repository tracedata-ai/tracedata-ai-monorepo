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
        <DashboardSection gridCols={4} className="py-8">
          <div className="col-span-1 lg:col-span-4 flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
            <div>
              <h1 className="text-3xl font-black text-slate-900 tracking-tight">{issue.summary}</h1>
              <p className="text-muted-foreground font-medium mt-2 flex items-center gap-2">
                <span className="text-slate-900 font-bold">{issue.assetName}</span> (ID: {issue.vehicleId})
              </p>
            </div>
            
            {/* Status Button/Badge */}
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase border shadow-sm ${
                 issue.status === "Resolved"
                 ? "bg-emerald-50 text-emerald-600 border-emerald-100"
                 : "bg-amber-50 text-amber-600 border-amber-100"
             }`}>
              {issue.status === "Resolved" && <div className="w-2 h-2 rounded-full bg-emerald-500"></div>}
              {issue.status === "Open" && <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>}
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
              >
                {issue.agentReasoning}
                {issue.agentTags && (
                  <div className="mt-6 flex flex-wrap gap-2">
                    {issue.agentTags.map((tag) => (
                      <span key={tag} className="px-3 py-1 bg-white text-brand-blue text-xs font-bold rounded-lg border border-brand-blue/10 shadow-sm uppercase tracking-tighter">
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
            >
              <div className="relative pl-8 border-l-2 border-slate-100 dark:border-slate-800 space-y-10 ml-2">
                {issue.timeline.map((event, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-[41px] top-1 w-4 h-4 bg-white dark:bg-slate-900 border-2 border-slate-200 dark:border-slate-700 group-hover:border-brand-blue transition-colors rounded-full z-10"></div>
                    <div>
                      <p className="text-base font-bold text-slate-900 group-hover:text-brand-blue transition-colors">
                        {event.title}
                      </p>
                      <p className="text-xs text-brand-blue font-bold mt-1 uppercase tracking-widest font-mono">
                        {event.timestamp}
                      </p>
                      <p className="text-sm text-slate-500 mt-3 leading-relaxed max-w-2xl">
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
