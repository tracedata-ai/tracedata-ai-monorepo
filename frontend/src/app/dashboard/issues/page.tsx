"use client";

import { useState } from "react";
import { dashboardConfig, IssueRecord } from "@/config/dashboard";
import {
  Download,
  Plus,
  Truck,
  Brain,
  ExternalLink,
  AlertTriangle,
  CheckCircle2,
  Clock,
  History,
  Wrench
} from "lucide-react";
import { cn } from "@/lib/utils";

import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { MetricCard } from "@/components/shared/MetricCard";
import { issueColumns } from "./issue-columns";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";

function IssueDetailContent({ issue }: { issue: IssueRecord }) {
  return (
    <DetailContentTemplate
      heroIcon={Truck}
      heroTitle={issue.assetName}
      heroSubtitle={issue.vehicleId}
      highlights={[
        {
          label: "Current Status",
          value: issue.status,
          className: cn(
            issue.status === 'Resolved' ? 'text-brand-teal' :
            issue.status === 'Open' ? 'text-amber-500' :
            'text-slate-400'
          )
        },
        {
          label: "Priority Level",
          value: issue.priority,
          className: cn(
            issue.priority === 'Critical' ? 'text-rose-500' :
            issue.priority === 'High' ? 'text-amber-500' :
            'text-slate-500'
          )
        }
      ]}
    >
      <div className="space-y-6">
        {/* AI Insight Section */}
        {issue.agentReasoning && (
          <FeatureCard
            title={`AI Diagnostics (${issue.agent})`}
            icon={Brain}
            variant="brand"
            isNarrative
          >
            {issue.agentReasoning}
            {issue.agentTags && (
              <div className="mt-4 flex flex-wrap gap-2">
                {issue.agentTags.map((tag) => (
                  <span key={tag} className="px-2 py-0.5 bg-white text-brand-blue text-[10px] font-bold rounded uppercase tracking-tighter border border-brand-blue/10">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </FeatureCard>
        )}

        {/* Resolution Data */}
        {issue.status === "Resolved" && (
          <InfoCard
            title="Resolution Data"
            icon={CheckCircle2}
            items={[
              { label: "Technician", value: issue.technician },
              { label: "Action Taken", value: issue.resolutionAction, className: "col-span-2" }
            ]}
          />
        )}

        {/* Timeline */}
        <FeatureCard
          title="Event Timeline"
          icon={History}
        >
          <div className="relative pl-6 border-l-2 border-slate-200 dark:border-slate-800 space-y-6">
            {issue.timeline.map((event, idx) => (
              <div key={idx} className="relative">
                <div className="absolute -left-[31px] top-0 w-4 h-4 bg-slate-300 dark:bg-slate-700 rounded-full ring-4 ring-white dark:ring-slate-900"></div>
                <div>
                  <p className="text-xs font-bold text-foreground">{event.title}</p>
                  <p className="text-[10px] text-brand-blue font-bold uppercase tracking-wider mt-0.5">{event.timestamp}</p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{event.description}</p>
                </div>
              </div>
            ))}
          </div>
        </FeatureCard>
      </div>
    </DetailContentTemplate>
  );
}

export default function IssuesPage() {
  const { issues } = dashboardConfig;
  const [activeTab, setActiveTab] = useState("Open");
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  const selectedIssue = issues.find(i => i.id === selectedIssueId) || null;
  const filteredIssues = issues.filter(i => i.status === activeTab);

  // Statistics for MetricCards
  const criticalCount = issues.filter(i => i.priority === 'Critical' && i.status !== 'Resolved').length;
  const openCount = issues.filter(i => i.status === 'Open').length;
  const resolvedToday = issues.filter(i => i.status === 'Resolved').length;

  return (
    <DashboardPageTemplate
      title="Issues Hub"
      description="Manage fleet maintenance faults and real-time alerts."
      headerActions={
        <>
          <Button variant="outline" className="gap-2">
            <Download className="w-4 h-4" /> Export
          </Button>
          <Button className="gap-2">
            <Plus className="w-4 h-4" /> New Issue
          </Button>
        </>
      }
      stats={
        <>
          <MetricCard
            label="Active Critical"
            value={criticalCount}
            icon={AlertTriangle}
            iconColor="text-red-500"
            trend={{ value: 2, label: "v. yesterday", isPositive: false }}
          />
          <MetricCard
            label="Open Tickets"
            value={openCount}
            icon={Clock}
            trend={{ value: 5, label: "since Monday", isPositive: false }}
          />
          <MetricCard
            label="Resolved Today"
            value={resolvedToday}
            icon={CheckCircle2}
            iconColor="text-emerald-500"
            trend={{ value: 12, label: "matched SLA", isPositive: true }}
          />
        </>
      }
      filters={
        <div className="flex gap-8">
          {["Open", "Overdue", "Resolved", "Closed"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                "pb-3 border-b-2 text-sm font-bold transition-colors outline-none",
                activeTab === tab
                  ? "border-brand-blue text-brand-blue"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              )}
            >
              {tab}
            </button>
          ))}
        </div>
      }
    >
      <DataTable
        columns={issueColumns}
        data={filteredIssues}
        selectedId={selectedIssueId}
        onRowClick={(issue) => setSelectedIssueId(issue.id)}
      />

      <DetailSheet
        isOpen={!!selectedIssueId}
        onClose={() => setSelectedIssueId(null)}
        title="Issue Detail View"
        deepLink={selectedIssue ? `/dashboard/issues/${selectedIssue.id}` : undefined}
      >
        {selectedIssue && <IssueDetailContent issue={selectedIssue} />}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}

