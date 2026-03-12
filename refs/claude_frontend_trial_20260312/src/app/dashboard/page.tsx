"use client";

import { AgentPulse } from "@/components/dashboard/AgentPulse";
import { FleetEquilibrium } from "@/components/dashboard/FleetEquilibrium";
import { LiveOrchestration } from "@/components/dashboard/LiveOrchestration";
import { BurnoutForecast } from "@/components/dashboard/BurnoutForecast";
import { AdvocacyAppeals } from "@/components/dashboard/AdvocacyAppeals";

export default function DashboardOverview() {
  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="dashboard-overview-page">
      
      {/* Top Strip: Agent Status */}
      <AgentPulse />
      
      {/* 2nd Row: Core Metrics & Live Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 h-full">
          <FleetEquilibrium />
        </div>
        <div className="lg:col-span-8 h-full">
          <LiveOrchestration />
        </div>
      </div>
      
      {/* 3rd Row: Predictive & Human Intervention */}
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
