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

import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { MetricCard } from "@/components/shared/MetricCard";
import { GlassCard } from "@/components/shared/GlassCard";
import { issueColumns } from "./issue-columns";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";
function IssueDetailContent({ issue }: { issue: IssueRecord }) {
  return (
    <div className="space-y-6">
      <DashboardSection gridCols={1} isFullWidth className="px-6 py-0 pb-4 border-b border-border">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-lg bg-brand-blue/10 flex items-center justify-center text-brand-blue">
            <Truck className="w-6 h-6" />
          </div>
          <div>
            <h4 className="font-bold text-foreground text-lg leading-tight">{issue.assetName}</h4>
            <p className="text-xs text-muted-foreground font-bold tracking-widest uppercase font-mono mt-1">{issue.vehicleId}</p>
          </div>
        </div>
        
        <InfoCard
          items={[
            { 
              label: "Status", 
              value: (
                <span className={issue.status === "Resolved" ? "text-brand-teal" : "text-amber-600"}>
                  {issue.status}
                </span>
              )
            },
            { 
              label: "Priority", 
              value: (
                <span className={
                  issue.priority === "Critical" ? "text-red-600" : 
                  issue.priority === "High" ? "text-orange-600" : "text-slate-600"
                }>
                  {issue.priority}
                </span>
              )
            }
          ]}
          className="p-3 !bg-transparent !border-0 !shadow-none !p-0"
        />
      </DashboardSection>

      <div className="p-6 space-y-6">
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
    </div>
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
  const resolvedToday = issues.filter(i => i.status === 'Resolved').length; // Mock simplified

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      <header className="bg-white dark:bg-slate-900 border-b border-border flex-shrink-0">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <div>
              <h2 className="text-3xl font-black text-slate-900 tracking-tight flex items-center gap-3">
                Issues Hub
              </h2>
              <p className="text-muted-foreground mt-1 text-sm">Manage and track fleet maintenance faults and real-time alerts.</p>
            </div>
            <div className="flex gap-3">
              <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-border rounded-lg text-sm font-semibold hover:bg-slate-50 transition-colors">
                <Download className="w-4 h-4" /> Export
              </button>
              <button className="flex items-center gap-2 px-4 py-2 bg-brand-blue text-white rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
                <Plus className="w-4 h-4" /> New Issue
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
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
          </div>

          <div className="mt-8 flex gap-8">
            {["Open", "Overdue", "Resolved", "Closed"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`pb-3 border-b-2 text-sm font-bold transition-colors ${
                  activeTab === tab
                    ? "border-brand-blue text-brand-blue"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </DashboardSection>
      </header>

      <main className="flex-1 overflow-auto bg-slate-50/50 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-8">
          <DataTable
            columns={issueColumns}
            data={filteredIssues}
            selectedId={selectedIssueId}
            onRowClick={(issue) => setSelectedIssueId(issue.id)}
          />
        </DashboardSection>
      </main>

      <DetailSheet
        isOpen={!!selectedIssueId}
        onClose={() => setSelectedIssueId(null)}
        title="Issue Detail View"
        deepLink={selectedIssue ? `/dashboard/issues/${selectedIssue.id}` : undefined}
      >
        {selectedIssue && <IssueDetailContent issue={selectedIssue} />}
      </DetailSheet>
    </div>
  );
}

