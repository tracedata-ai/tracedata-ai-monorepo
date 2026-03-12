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
  AlertCircle,
  ShieldAlert
} from "lucide-react";

import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

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
    <DashboardPageTemplate
      title={issue.summary}
      description={`${issue.assetName} • ${issue.id}`}
      breadcrumbs={
        <>
          <Link href="/dashboard/issues" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-3 h-3" />
            Issues Hub
          </Link>
          <ChevronRight className="w-3 h-3 mx-2 opacity-30" />
          <span className="text-slate-900">{issue.id}</span>
        </>
      }
      headerActions={
        <>
          <Button variant="outline" size="sm">Export Report</Button>
          <Button size="sm">Update Status</Button>
        </>
      }
    >
      <DetailContentTemplate
        heroIcon={AlertCircle}
        heroTitle={issue.summary}
        heroSubtitle={`${issue.assetName} • ${issue.id}`}
        highlights={[
          {
            label: "Priority",
            value: issue.priority,
            className: cn(
              issue.priority === "Critical" ? "text-rose-600" :
              issue.priority === "High" ? "text-amber-600" :
              "text-slate-600"
            )
          },
          {
            label: "Current Status",
            value: issue.status,
            className: cn(
              issue.status === "Resolved" ? "text-emerald-600" : "text-amber-500"
            )
          }
        ]}
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            {issue.agentReasoning && (
              <FeatureCard
                title={`AI Diagnostic Reasoning (${issue.agent})`}
                icon={Brain}
                variant="brand"
                isNarrative
              >
                <div className="space-y-6">
                  <div className="text-lg font-medium text-slate-900 leading-relaxed italic">
                    &ldquo;{issue.agentReasoning}&rdquo;
                  </div>
                  {issue.agentTags && (
                    <div className="flex flex-wrap gap-2 pt-4">
                      {issue.agentTags.map((tag) => (
                        <span key={tag} className="px-2.5 py-1 bg-white text-brand-blue text-[10px] font-bold rounded-lg border border-brand-blue/10 shadow-sm uppercase tracking-widest">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </FeatureCard>
            )}

            <FeatureCard
              title="Event Narrative Timeline"
              icon={History}
            >
              <div className="relative pl-8 border-l-2 border-slate-100 space-y-10 ml-1 mt-6">
                {issue.timeline.map((event, idx) => (
                  <div key={idx} className="relative group">
                    <div className="absolute -left-[37px] top-1 w-4 h-4 bg-white border-2 border-slate-200 group-hover:border-brand-blue transition-colors rounded-full z-10 shadow-sm"></div>
                    <div>
                      <div className="flex justify-between items-start mb-1">
                        <p className="text-sm font-bold text-slate-900 leading-none group-hover:text-brand-blue transition-colors">
                          {event.title}
                        </p>
                        <p className="text-[10px] text-brand-blue font-bold uppercase tracking-widest font-mono">
                          {event.timestamp}
                        </p>
                      </div>
                      <p className="text-xs text-slate-500 mt-2 leading-relaxed max-w-2xl">
                        {event.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </FeatureCard>
          </div>

          <div className="space-y-8">
            <InfoCard
              title="Properties"
              icon={ShieldAlert}
              items={[
                { label: "Fault Type", value: issue.type },
                { label: "Asset ID", value: issue.vehicleId, className: "font-mono" },
                { label: "Reported", value: issue.reportedDate, icon: Calendar }
              ]}
              columns={1}
            />

            {issue.status === "Resolved" && (
              <InfoCard
                title="Resolution Data"
                icon={CheckCircle2}
                variant="brand"
                items={[
                  { label: "Technician", value: issue.technician },
                  { label: "Action Taken", value: issue.resolutionAction },
                  { label: "Resolved Date", value: issue.resolvedDate, icon: Clock }
                ]}
                columns={1}
              />
            )}
          </div>
        </div>
      </DetailContentTemplate>
    </DashboardPageTemplate>
  );
}
