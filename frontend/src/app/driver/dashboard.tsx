/**
 * Driver Dashboard - Personalized view for drivers
 * Shows own trips, coaching, appeals, behavior insights
 */

"use client";

import React from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { BehaviorScoreBreakdown } from "@/components/explainability/BehaviorScoreBreakdown";
import { SHAPForcePlot } from "@/components/explainability/SHAPForcePlot";
import { useAuth } from "@/context/AuthContext";
import { TrendingUp, AlertTriangle, Target } from "lucide-react";
import {
  mockTripScores,
  mockSHAPData,
  mockDriverBehavior,
} from "@/lib/mock-data";

export default function DriverDashboard() {
  const { tenantId, role } = useAuth();
  const driverId = "driver_alice_001"; // In production, get from auth/query params

  const driverProfile = mockDriverBehavior[driverId];
  const latestScore = mockTripScores["trip_20250310_001"];
  const latestSHAP = mockSHAPData["trip_20250310_001"];

  if (!driverProfile) {
    return <div className="p-8">Driver profile not found.</div>;
  }

  return (
    <DashboardPageTemplate
      title="My Dashboard"
      description="Your driving performance and personalized insights"
      breadcrumbs={
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span>Driver Portal</span>
        </div>
      }
      stats={
        <>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-brand-blue" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Avg Score
                </p>
                <p className="text-2xl font-black text-foreground">
                  {driverProfile.averageScore.toFixed(1)}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <Target className="w-5 h-5 text-brand-teal" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Total Trips
                </p>
                <p className="text-2xl font-black text-foreground">
                  {driverProfile.totalTrips}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-brand-rose" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Risk Incidents
                </p>
                <p className="text-2xl font-black text-foreground">
                  {driverProfile.totalRiskIncidents}
                </p>
              </div>
            </div>
          </div>
        </>
      }
    >
      <div className="space-y-8">
        {/* Burnout Risk Alert */}
        {driverProfile.burnoutRiskLevel === 1 && (
          <section className="rounded-lg border border-red-200 bg-red-50 p-6">
            <h3 className="font-semibold text-red-900">
              ⚠️ Burnout Risk Detected
            </h3>
            <p className="mt-2 text-sm text-red-800">
              We've noticed some indicators that suggest you might be
              experiencing burnout. Please consider taking a break or reaching
              out to your fleet manager for support.
            </p>
            <ul className="mt-3 list-inside space-y-1 list-disc text-sm text-red-800">
              {driverProfile.burnoutIndicators.map((indicator, idx) => (
                <li key={idx}>{indicator}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Latest Trip Score with Breakdown */}
        {latestScore && (
          <section className="space-y-4">
            <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
              Latest Trip Score
            </h2>
            <BehaviorScoreBreakdown score={latestScore} />
          </section>
        )}

        {/* SHAP Explanation */}
        {latestSHAP && (
          <section className="space-y-4">
            <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
              Feature Importance (Why you got this score)
            </h2>
            <SHAPForcePlot data={latestSHAP} />
          </section>
        )}

        {/* Coaching History */}
        {driverProfile.coachingHistory.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
              Recent Coaching
            </h2>
            <div className="space-y-3">
              {driverProfile.coachingHistory.map((coaching, idx) => (
                <div
                  key={idx}
                  className={`rounded-lg border p-4 ${
                    coaching.tone === "encouraging"
                      ? "bg-teal-50 border-teal-200"
                      : "bg-yellow-50 border-yellow-200"
                  }`}
                >
                  <p
                    className={`font-semibold ${
                      coaching.tone === "encouraging"
                        ? "text-teal-900"
                        : "text-yellow-900"
                    }`}
                  >
                    {coaching.tone === "encouraging" ? "✓" : "→"}{" "}
                    {coaching.generatedCoaching}
                  </p>
                  <p className="mt-2 text-xs text-gray-600">
                    Trip: {coaching.tripId}
                    {coaching.driverAcknowledged && (
                      <span className="ml-2 text-teal-700 font-semibold">
                        • Acknowledged
                      </span>
                    )}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Emotional Trajectory */}
        {driverProfile.emotionalTrajectory.length > 0 && (
          <section className="space-y-4">
            <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
              Recent Feedback
            </h2>
            <div className="space-y-2">
              {driverProfile.emotionalTrajectory.map((data, idx) => (
                <div
                  key={idx}
                  className={`rounded p-3 text-sm ${
                    data.sentiment === "positive"
                      ? "bg-green-50 text-green-800"
                      : data.sentiment === "neutral"
                        ? "bg-gray-50 text-gray-800"
                        : "bg-red-50 text-red-800"
                  }`}
                >
                  <p className="font-medium">"{data.feedback}"</p>
                  <p className="text-xs mt-1 opacity-75">
                    {new Date(data.timestamp).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          </section>
        )}
      </div>
    </DashboardPageTemplate>
  );
}
