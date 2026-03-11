"use client";

import { useState } from "react";
import { dashboardConfig, IssueRecord } from "@/config/dashboard";
import {
  Download,
  Plus,
  ChevronsUp,
  ChevronUp,
  ChevronDown,
  Minus,
  Truck,
  Brain,
} from "lucide-react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";

export default function IssuesPage() {
  const [activeTab, setActiveTab] = useState("Open");
  const [selectedIssueId, setSelectedIssueId] = useState<string | null>(null);

  const selectedIssue = dashboardConfig.issues.find(
    (issue) => issue.id === selectedIssueId
  ) || null;

  const renderPriorityIcon = (priority: string) => {
    switch (priority) {
      case "Critical":
        return <ChevronsUp className="w-5 h-5 text-red-500" />;
      case "High":
        return <ChevronUp className="w-5 h-5 text-orange-500" />;
      case "Medium":
        return <Minus className="w-5 h-5 text-slate-400" />;
      case "Low":
        return <ChevronDown className="w-5 h-5 text-blue-500" />;
      default:
        return <Minus className="w-5 h-5 text-slate-400" />;
    }
  };

  const renderStatusBadge = (status: string) => {
    switch (status) {
      case "Resolved":
        return (
          <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs font-bold">
            Resolved
          </span>
        );
      case "Open":
        return (
          <span className="px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 rounded-full text-xs font-bold">
            Open
          </span>
        );
      case "Overdue":
        return (
          <span className="px-3 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 rounded-full text-xs font-bold">
            Overdue
          </span>
        );
      case "Closed":
        return (
          <span className="px-3 py-1 bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 rounded-full text-xs font-bold">
            Closed
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Header Section */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-6 flex-shrink-0">
        <div className="flex flex-wrap justify-between items-center gap-4">
          <div>
            <h2 className="text-3xl font-black text-foreground tracking-tight">
              Issues
            </h2>
            <p className="text-muted-foreground mt-1 text-sm">
              Manage and track fleet maintenance faults and real-time alerts.
            </p>
          </div>
          <div className="flex gap-3">
            <button className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 border border-border rounded-lg text-sm font-semibold hover:bg-slate-50 dark:hover:bg-slate-800/80 transition-colors">
              <Download className="w-4 h-4" />
              Export Data
            </button>
            <button className="flex items-center gap-2 px-4 py-2 bg-brand-blue text-white rounded-lg text-sm font-semibold hover:bg-brand-blue/90 shadow-sm transition-colors">
              <Plus className="w-4 h-4" />
              Log New Issue
            </button>
          </div>
        </div>

        {/* Tabs */}
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
      </header>

      {/* Content Area with Table and Quick View */}
      <div className="flex-1 overflow-auto p-8">
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-border overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-slate-50 dark:bg-slate-800/50">
              <TableRow className="border-b border-border hover:bg-transparent">
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Priority
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Name
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Type
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Issue #
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Summary
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  AI Agent
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Status
                </TableHead>
                <TableHead className="px-6 py-4 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Reported
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody className="divide-y divide-border">
              {dashboardConfig.issues.map((issue) => (
                <TableRow
                  key={issue.id}
                  onClick={() => setSelectedIssueId(issue.id)}
                  className={`cursor-pointer transition-colors ${
                    selectedIssueId === issue.id ? "bg-brand-blue/5" : "hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  }`}
                >
                  <TableCell className="px-6 py-4">
                    {renderPriorityIcon(issue.priority)}
                  </TableCell>
                  <TableCell className="px-6 py-4 font-semibold text-foreground">
                    {issue.assetName}
                  </TableCell>
                  <TableCell className="px-6 py-4 text-sm text-muted-foreground">
                    {issue.type}
                  </TableCell>
                  <TableCell className="px-6 py-4 text-sm text-muted-foreground">
                    {issue.id}
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    <span className="px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded text-xs font-medium text-slate-600 dark:text-slate-300">
                      {issue.summary}
                    </span>
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    {issue.agent === "Safety Agent" ? (
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-xs font-bold text-brand-blue px-2 py-1 bg-brand-blue/10 rounded-full">
                          {issue.agent}
                        </span>
                      </div>
                    ) : (
                      <span className="text-xs font-bold text-muted-foreground px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded-full">
                        {issue.agent}
                      </span>
                    )}
                  </TableCell>
                  <TableCell className="px-6 py-4">
                    {renderStatusBadge(issue.status)}
                  </TableCell>
                  <TableCell className="px-6 py-4 text-sm text-muted-foreground">
                    {issue.reportedDate}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>

      <Sheet open={!!selectedIssueId} onOpenChange={(open) => !open && setSelectedIssueId(null)}>
        <SheetContent className="w-full sm:max-w-md bg-white dark:bg-slate-900 border-l border-border flex flex-col overflow-y-auto p-0 gap-0 shadow-xl">
          <SheetHeader className="sr-only">
            <SheetTitle>Issue Details</SheetTitle>
          </SheetHeader>
          
          {selectedIssue && (
            <div className="flex flex-col h-full mt-8">
              {/* Header */}
              <div className="p-6 pt-2 border-b border-border">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-bold text-foreground tracking-tight">
                    Issue Details
                  </h3>
                </div>

                <div className="flex items-center gap-4 mb-6">
                  <div className="w-12 h-12 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                    <Truck className="w-6 h-6 text-slate-600 dark:text-slate-400" />
                  </div>
                  <div>
                    <h4 className="font-bold text-foreground">
                      {selectedIssue.assetName}
                    </h4>
                    <p className="text-xs text-muted-foreground font-medium uppercase">
                      ID: {selectedIssue.vehicleId}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">
                      Status
                    </p>
                    <p
                      className={`text-sm font-bold uppercase ${
                        selectedIssue.status === "Resolved"
                          ? "text-green-600 dark:text-green-400"
                          : "text-amber-600 dark:text-amber-400"
                      }`}
                    >
                      {selectedIssue.status}
                    </p>
                  </div>
                  <div className="p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">
                      Priority
                    </p>
                    <p
                      className={`text-sm font-bold uppercase ${
                        selectedIssue.priority === "Critical"
                          ? "text-red-600 dark:text-red-400"
                          : selectedIssue.priority === "High"
                          ? "text-orange-600 dark:text-orange-400"
                          : selectedIssue.priority === "Medium"
                          ? "text-slate-600 dark:text-slate-400"
                          : "text-blue-600 dark:text-blue-400"
                      }`}
                    >
                      {selectedIssue.priority}
                    </p>
                  </div>
                </div>
              </div>

              {/* AI Context & Timeline */}
              <div className="p-6 space-y-8">
                {/* Resolution Summary */}
                {selectedIssue.status === "Resolved" && (
                  <div>
                    <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-4">
                      Resolution Summary
                    </h5>
                    <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-border space-y-3">
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase font-bold">
                          Technician
                        </p>
                        <p className="text-sm font-semibold text-foreground mt-0.5">
                          {selectedIssue.technician}
                        </p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase font-bold">
                          Action Taken
                        </p>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                          {selectedIssue.resolutionAction}
                        </p>
                      </div>
                      <div>
                        <p className="text-[10px] text-slate-500 uppercase font-bold">
                          Resolved Date
                        </p>
                        <p className="text-sm text-slate-600 dark:text-slate-400 font-medium mt-0.5">
                          {selectedIssue.resolvedDate}
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                {/* AI Reasoning */}
                {selectedIssue.agentReasoning && (
                  <div>
                    <h5 className="text-xs font-bold text-foreground uppercase tracking-wider mb-4 flex items-center gap-2">
                      <Brain className="w-4 h-4 text-brand-blue" />
                      AI Reasoning ({selectedIssue.agent})
                    </h5>
                    <div className="relative pl-6 border-l-2 border-brand-blue/20">
                      <div className="absolute -left-[9px] top-0 w-4 h-4 bg-brand-blue rounded-full ring-4 ring-white dark:ring-slate-900"></div>
                      <div className="bg-brand-blue/5 p-4 rounded-xl border border-brand-blue/10">
                        <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed italic">
                          &quot;{selectedIssue.agentReasoning}&quot;
                        </p>
                        {selectedIssue.agentTags && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {selectedIssue.agentTags.map((tag) => (
                              <span
                                key={tag}
                                className="px-2 py-0.5 bg-brand-blue/20 text-brand-blue text-[10px] font-bold rounded"
                              >
                                {tag}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Fault Timeline */}
                {selectedIssue.timeline && selectedIssue.timeline.length > 0 && (
                  <div>
                    <h5 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-4">
                      Fault Timeline
                    </h5>
                    <div className="relative pl-6 border-l-2 border-slate-200 dark:border-slate-800 space-y-6">
                      {selectedIssue.timeline.map((event, idx) => (
                        <div key={idx} className="relative">
                          <div className="absolute -left-[31px] top-0 w-4 h-4 bg-slate-300 dark:bg-slate-700 rounded-full ring-4 ring-white dark:ring-slate-900"></div>
                          <div>
                            <p className="text-xs font-bold text-foreground">
                              {event.title}
                            </p>
                            <p className="text-xs text-slate-500 mt-0.5">
                              {event.timestamp}
                            </p>
                            <p className="text-sm text-slate-600 dark:text-slate-400 mt-1.5">
                              {event.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}

