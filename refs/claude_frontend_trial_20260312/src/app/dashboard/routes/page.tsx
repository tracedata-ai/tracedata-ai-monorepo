"use client";

import { useState } from "react";
import { dashboardConfig, RouteRecord } from "@/config/dashboard";
import { Route, Map, MapPin, Clock, TrendingUp, Search } from "lucide-react";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { routeColumns } from "./route-columns";
import { MetricCard } from "@/components/shared/MetricCard";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

function RouteDetailContent({ route }: { route: RouteRecord }) {
  return (
    <DetailContentTemplate
      heroIcon={Map}
      heroTitle={route.id}
      heroSubtitle={route.name}
      highlights={[
        {
          label: "Status",
          value: "Active",
          className: 'text-brand-teal'
        },
        {
          label: "Avg. Duration",
          value: `${route.historicalAvgMins} mins`,
          icon: Clock,
          iconColor: "text-amber-500"
        }
      ]}
    >
      <div className="space-y-6">
        <InfoCard
          title="Physical Parameters"
          icon={MapPin}
          items={[
            { label: "Total Distance", value: `${route.standardDistanceKm} km` },
            { label: "Complexity", value: route.standardDistanceKm > 50 ? "High" : "Standard" }
          ]}
        />

        <InfoCard
          title="Performance Registry"
          icon={TrendingUp}
          items={[
            { label: "Total Trips Run", value: route.totalTripsCompleted },
            { label: "Optimal Time", value: `${Math.round(route.historicalAvgMins * 0.9)} mins` }
          ]}
        />

        <FeatureCard
          title="Route Path Definition"
          icon={Route}
        >
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600 text-[10px] font-bold border border-emerald-100 flex-shrink-0 mt-0.5">A</div>
              <div>
                <p className="text-xs font-bold text-foreground capitalize">{route.id.split('-')[1]?.toLowerCase() || 'Origin'} Hub</p>
                <p className="text-[10px] text-muted-foreground">Primary loading zone</p>
              </div>
            </div>
            <div className="w-[1px] h-6 bg-slate-200 ml-3"></div>
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-rose-50 flex items-center justify-center text-rose-600 text-[10px] font-bold border border-rose-100 flex-shrink-0 mt-0.5">B</div>
              <div>
                <p className="text-xs font-bold text-foreground capitalize">{route.id.split('-')[2]?.toLowerCase() || 'Destination'} Terminal</p>
                <p className="text-[10px] text-muted-foreground">Delivery point</p>
              </div>
            </div>
          </div>
        </FeatureCard>
      </div>
    </DetailContentTemplate>
  );
}

export default function RoutesPage() {
  const { routes } = dashboardConfig;
  const [selectedRouteId, setSelectedRouteId] = useState<string | null>(null);
  const selectedRoute = routes.find(r => r.id === selectedRouteId) || null;

  return (
    <DashboardPageTemplate
      title="Route Repository"
      description="Define and manage logistics corridors and baseline performance."
      headerActions={
        <>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input type="text" placeholder="Search routes..." className="pl-9 pr-4 py-2 bg-background border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue" />
          </div>
          <Button>Create Route</Button>
        </>
      }
      stats={
        <>
          <MetricCard
            label="Active Corridors"
            value={routes.length}
            icon={Route}
            iconColor="text-brand-blue"
          />
          <MetricCard
            label="Total Network"
            value={`${routes.reduce((acc, curr) => acc + curr.standardDistanceKm, 0).toLocaleString()} km`}
            icon={Map}
            iconColor="text-brand-teal"
          />
          <MetricCard
            label="Efficiency Index"
            value="94%"
            icon={TrendingUp}
            iconColor="text-amber-500"
            trend={{ value: 3, label: "optimizing", isPositive: true }}
          />
        </>
      }
    >
      <DataTable
        columns={routeColumns}
        data={routes}
        selectedId={selectedRouteId}
        onRowClick={(route) => setSelectedRouteId(route.id)}
      />

      <DetailSheet
        isOpen={!!selectedRouteId}
        onClose={() => setSelectedRouteId(null)}
        title="Route Detail Configuration"
        deepLink={selectedRoute ? `/dashboard/routes/${selectedRoute.id}` : undefined}
      >
        {selectedRoute && <RouteDetailContent route={selectedRoute} />}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}
