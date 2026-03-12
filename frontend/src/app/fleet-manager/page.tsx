"use client";

import React from "react";
import { AgentPulse } from "@/components/dashboard/AgentPulse";
import { FleetEquilibrium } from "@/components/dashboard/FleetEquilibrium";
import { LiveOrchestration } from "@/components/dashboard/LiveOrchestration";
import { BurnoutForecast } from "@/components/dashboard/BurnoutForecast";
import { AdvocacyAppeals } from "@/components/dashboard/AdvocacyAppeals";
import { OrchestratorView } from "@/components/agents/OrchestratorView";
import { SafetyAlertPanel } from "@/components/agents/SafetyAlertPanel";

export default function DashboardOverview() {
  // Mock tenant for POC (in production, extract from auth context)
  const tenantId = "tenant_demo_001";

  return (
    <div
      className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20"
      data-purpose="dashboard-overview-page"
    >
      {/* Top Strip: Agent Status */}
      <AgentPulse />

      {/* Safety Alerts & Orchestrator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SafetyAlertPanel tenantId={tenantId} />
        <OrchestratorView />
      </div>

      {/* Core Metrics & Live Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 h-full">
          <FleetEquilibrium />
        </div>
        <div className="lg:col-span-8 h-full">
          <LiveOrchestration />
        </div>
      </div>

      {/* Predictive & Human Intervention */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 pb-12">
        <div className="lg:col-span-4 h-full">
          <BurnoutForecast />
        </div>
        <div className="lg:col-span-8 h-full">
          <AdvocacyAppeals />
        </div>
      </div>
    </div>
  );
}
