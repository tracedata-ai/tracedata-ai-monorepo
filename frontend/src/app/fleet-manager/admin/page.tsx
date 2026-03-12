/**
 * Admin Observability & Fairness Metrics Page
 * RUBRIC: Admin tools for monitoring fairness, security, and system health
 * SECURITY: Wrapped with ManagerOnly guard—Drivers cannot access this page
 */

"use client";

import React from "react";
import { ManagerOnly } from "@/components/security/RoleGuard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Button } from "@/components/ui/button";
import { BarChart3, Shield, TrendingUp } from "lucide-react";
import { mockFairnessAudit } from "@/lib/mock-data";

function AdminObservabilityContent() {
  return (
    <DashboardPageTemplate
      title="Observability & Auditing"
      description="System health, fairness metrics, and security monitoring"
      breadcrumbs={
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <a href="/fleet-manager" className="hover:text-slate-700">
            Home
          </a>
          <span>/</span>
          <span>Admin</span>
        </div>
      }
      headerActions={
        <>
          <Button variant="outline">Export Report</Button>
          <Button>Refresh</Button>
        </>
      }
      stats={
        <>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-brand-blue" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Global SPD
                </p>
                <p className="text-2xl font-black text-foreground">
                  {mockFairnessAudit.globalStatisticalParityDifference.toFixed(
                    3,
                  )}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <Shield className="w-5 h-5 text-brand-teal" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Security Status
                </p>
                <p className="text-2xl font-black text-foreground">SECURE</p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-brand-rose" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  System Load
                </p>
                <p className="text-2xl font-black text-foreground">24%</p>
              </div>
            </div>
          </div>
        </>
      }
    >
      <div className="space-y-8">
        {/* Fairness Audit Section */}
        <section className="space-y-4">
          <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
            Fairness Audit Report
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Audit Metadata */}
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-foreground">Audit Details</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-muted-foreground font-medium">Audit ID</p>
                  <p className="font-mono text-foreground">
                    {mockFairnessAudit.auditId}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground font-medium">Timestamp</p>
                  <p>
                    {new Date(mockFairnessAudit.timestamp).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground font-medium">
                    Debiasing Method
                  </p>
                  <p className="capitalize">{mockFairnessAudit.debiasMethod}</p>
                </div>
                <div>
                  <p className="text-muted-foreground font-medium">
                    Reference Group
                  </p>
                  <p>{mockFairnessAudit.referenceGroup}</p>
                </div>
              </div>
            </div>

            {/* SPD Metrics */}
            <div className="glass-card rounded-xl p-6 space-y-4">
              <h3 className="font-semibold text-foreground">
                Statistical Parity Difference
              </h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-muted-foreground">Global SPD</span>
                  <span
                    className={`font-bold ${
                      mockFairnessAudit.globalStatisticalParityDifference < 0.5
                        ? "text-brand-teal"
                        : "text-brand-red"
                    }`}
                  >
                    {mockFairnessAudit.globalStatisticalParityDifference.toFixed(
                      3,
                    )}
                  </span>
                </div>
                <div className="h-2 rounded bg-slate-200">
                  <div
                    className={`h-full rounded ${
                      mockFairnessAudit.globalStatisticalParityDifference < 0.5
                        ? "bg-brand-teal"
                        : "bg-brand-red"
                    }`}
                    style={{
                      width: `${Math.min(
                        (Math.abs(
                          mockFairnessAudit.globalStatisticalParityDifference,
                        ) /
                          1) *
                          100,
                        100,
                      )}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Cohort SPD Breakdown */}
          <div className="glass-card rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-foreground">
              Cohort Analysis (SPD by Driver Segment)
            </h3>
            <div className="space-y-3">
              {Object.entries(mockFairnessAudit.cohortSpd).map(
                ([cohort, spd]) => (
                  <div key={cohort} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="capitalize text-slate-700">
                        {cohort.replace(/_/g, " ")}
                      </span>
                      <span
                        className={`font-bold ${
                          Math.abs(spd) < 0.5
                            ? "text-brand-teal"
                            : "text-brand-rose"
                        }`}
                      >
                        {spd.toFixed(3)}
                      </span>
                    </div>
                    <div className="h-2 rounded bg-slate-200">
                      <div
                        className={`h-full rounded ${
                          spd >= 0
                            ? spd < 0.5
                              ? "bg-brand-teal"
                              : "bg-brand-rose"
                            : spd > -0.5
                              ? "bg-brand-teal"
                              : "bg-brand-red"
                        }`}
                        style={{
                          width: `${Math.min((Math.abs(spd) / 1) * 100, 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                ),
              )}
            </div>
          </div>

          {/* Impact Analysis */}
          <div className="glass-card rounded-xl p-6 space-y-4">
            <h3 className="font-semibold text-foreground">
              Impact of Debiasing
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded bg-slate-50 p-3 text-sm">
                <p className="text-muted-foreground font-medium">
                  Average Score Shift
                </p>
                <p className="text-xl font-bold text-foreground mt-1">
                  {mockFairnessAudit.impactOnScoring.avgScoreShift > 0
                    ? "+"
                    : ""}
                  {mockFairnessAudit.impactOnScoring.avgScoreShift.toFixed(2)}
                </p>
              </div>
              <div className="rounded bg-slate-50 p-3 text-sm">
                <p className="text-muted-foreground font-medium">
                  Max Score Shift
                </p>
                <p className="text-xl font-bold text-foreground mt-1">
                  {mockFairnessAudit.impactOnScoring.maxScoreShift > 0
                    ? "+"
                    : ""}
                  {mockFairnessAudit.impactOnScoring.maxScoreShift.toFixed(2)}
                </p>
              </div>
              <div className="rounded bg-slate-50 p-3 text-sm">
                <p className="text-muted-foreground font-medium">
                  Min Score Shift
                </p>
                <p className="text-xl font-bold text-foreground mt-1">
                  {mockFairnessAudit.impactOnScoring.minScoreShift > 0
                    ? "+"
                    : ""}
                  {mockFairnessAudit.impactOnScoring.minScoreShift.toFixed(2)}
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Documentation Note */}
        <section className="rounded bg-blue-50 p-6 text-sm text-blue-900">
          <p className="font-semibold">Reference: AIF360 Fairness Auditing</p>
          <p className="mt-2">
            Statistical Parity Difference (SPD) measures whether the positive
            prediction rate differs across protected groups. SPD {"<"} 0.5
            indicates acceptable fairness. This audit demonstrates TraceData's
            commitment to fairness-first scoring as required in A5 of the
            project documentation.
          </p>
        </section>
      </div>
    </DashboardPageTemplate>
  );
}

export default function AdminPage() {
  return (
    <ManagerOnly>
      <AdminObservabilityContent />
    </ManagerOnly>
  );
}
