/**
 * Driver Profile Page - Shows driver's personal profile
 */

"use client";

import React from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { useAuth } from "@/context/AuthContext";
import { User, Calendar, Award } from "lucide-react";
import { mockDrivers, mockDriverBehavior } from "@/lib/mock-data";

export default function DriverProfile() {
  const driverId = "driver_alice_001"; // In production, get from auth
  const driver = mockDrivers.find((d) => d.id === driverId);
  const profile = mockDriverBehavior[driverId];

  if (!driver || !profile) {
    return <div className="p-8">Profile not found.</div>;
  }

  return (
    <DashboardPageTemplate
      title="My Profile"
      description="Personal information and performance summary"
      breadcrumbs={
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <a href="/driver" className="hover:text-slate-700">
            Dashboard
          </a>
          <span>/</span>
          <span>Profile</span>
        </div>
      }
    >
      <div className="space-y-8">
        {/* Profile Hero */}
        <section>
          <DetailContentTemplate
            heroIcon={User}
            heroTitle={driver.name}
            heroSubtitle="Driver ID"
            highlights={[
              { label: "Total Trips", value: profile.totalTrips },
              { label: "Avg Score", value: profile.averageScore.toFixed(1) },
              { label: "Status", value: driver.status },
              { label: "Risk Incidents", value: profile.totalRiskIncidents },
            ]}
          >
            <div className="rounded bg-slate-50 p-4 text-sm space-y-3">
              <div>
                <p className="text-muted-foreground font-medium">Email</p>
                <p className="font-mono text-foreground">{driver.email}</p>
              </div>
              <div>
                <p className="text-muted-foreground font-medium">Driver ID</p>
                <p className="font-mono text-foreground">{driver.id}</p>
              </div>
            </div>
          </DetailContentTemplate>
        </section>

        {/* Performance Summary */}
        <section className="space-y-4">
          <h2 className="text-xl font-black uppercase tracking-tight text-foreground">
            Performance Summary
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass-card rounded-xl p-6 space-y-3">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Award className="w-5 h-5 text-brand-teal" />
                Achievements
              </h3>
              <div className="text-sm text-slate-700">
                <p>✓ {profile.totalTrips} completed trips</p>
                <p>✓ Average score: {profile.averageScore.toFixed(1)}/100</p>
                {profile.burnoutRiskLevel === 0 && (
                  <p>✓ Healthy burnout status</p>
                )}
              </div>
            </div>

            <div className="glass-card rounded-xl p-6 space-y-3">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Calendar className="w-5 h-5 text-brand-blue" />
                Status
              </h3>
              <div className="text-sm text-slate-700">
                <p>
                  Status:{" "}
                  <span className="font-semibold text-brand-teal">Active</span>
                </p>
                <p>Recent Activity: Consistent</p>
                <p>Support Available: Yes</p>
              </div>
            </div>
          </div>
        </section>

        {/* Support Note */}
        <section className="rounded-lg bg-blue-50 border border-blue-200 p-6 text-sm text-blue-900">
          <p className="font-semibold">Need Help?</p>
          <p className="mt-2">
            If you have questions about your scores, coaching feedback, or need
            to appeal a trip decision, please visit the Appeals section or
            contact your fleet manager.
          </p>
        </section>
      </div>
    </DashboardPageTemplate>
  );
}
