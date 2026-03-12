"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig, RouteRecord } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  Map,
  Activity,
  Target,
  ArrowRight,
  Navigation,
  Clock,
  TrendingUp,
  MapPin,
  Route as RouteIcon
} from "lucide-react";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { MetricCard } from "@/components/shared/MetricCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function RouteDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const routeId = resolvedParams.id;
  
  const route = dashboardConfig.routes.find((r) => r.id === routeId);
  
  if (!route) {
    notFound();
  }

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  return (
    <DashboardPageTemplate
      title={route.name}
      description={`Logistics Corridor Analysis • ${route.id}`}
      breadcrumbs={
        <>
          <Link href="/dashboard/routes" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-3 h-3" />
            Route Catalog
          </Link>
          <ChevronRight className="w-3 h-3 mx-2 opacity-30" />
          <span className="text-slate-900">{route.id}</span>
        </>
      }
      headerActions={
        <>
          <Button variant="outline" size="sm">History</Button>
          <Button size="sm">Edit Path</Button>
        </>
      }
    >
      <DetailContentTemplate
        heroIcon={Map}
        heroTitle={route.name}
        heroSubtitle={route.id}
        highlights={[
          {
            label: "Asset Status",
            value: "Active Corridor",
            className: "text-brand-teal"
          },
          {
            label: "Baseline Efficiency",
            value: "94.2%",
            icon: TrendingUp,
            iconColor: "text-amber-500"
          }
        ]}
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <FeatureCard
              title="Physical Path Definition"
              icon={Navigation}
            >
               <div className="mt-6 flex flex-col md:flex-row items-center gap-8 md:gap-4 px-2">
                  <div className="flex-1 w-full bg-slate-50 p-6 rounded-3xl border border-slate-100 flex flex-col gap-1">
                     <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400">Loading Node (Origin)</p>
                     <p className="text-xl font-bold text-slate-900">{route.origin}</p>
                  </div>
                  
                  <div className="p-2 bg-brand-blue/5 rounded-full">
                    <ArrowRight className="w-5 h-5 text-brand-blue rotate-90 md:rotate-0" />
                  </div>

                  <div className="flex-1 w-full bg-brand-blue/[0.03] p-6 rounded-3xl border border-brand-blue/10 flex flex-col gap-1">
                     <p className="text-[10px] font-bold uppercase tracking-widest text-brand-blue/60">Delivery Node (Destination)</p>
                     <p className="text-xl font-bold text-slate-900">{route.destination}</p>
                  </div>
               </div>
               
               <div className="mt-8 pt-6 border-t border-slate-100 flex justify-between items-center text-xs">
                 <div className="flex items-center gap-3">
                   <div className="w-2 h-2 rounded-full bg-brand-teal animate-pulse" />
                   <span className="text-slate-400 font-bold uppercase tracking-widest">Live Optimization Active</span>
                 </div>
                 <Button variant="ghost" size="sm" className="text-brand-blue">View Mapping</Button>
               </div>
            </FeatureCard>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
               <MetricCard
                  label="Avg Historical Time"
                  value={formatMinsToHours(route.historicalAvgMins)}
                  icon={Clock}
                  iconColor="text-brand-teal"
                  subValue="Stable performance"
               />
               <MetricCard
                  label="Baseline Distance"
                  value={`${route.standardDistanceKm.toFixed(1)} km`}
                  icon={MapPin}
                  subValue="Optimized corridors"
               />
            </div>
          </div>

          <div className="space-y-8">
            <InfoCard
              title="Operational Insights"
              icon={Target}
              variant="brand"
              items={[
                { label: "Total Trips Completed", value: route.totalTripsCompleted.toLocaleString(), className: "text-2xl font-black text-brand-teal col-span-2" }
              ]}
            >
               <p className="text-[10px] text-slate-500 leading-relaxed font-bold uppercase tracking-widest mt-6 border-t border-brand-teal/10 pt-6">
                  Primary Routing Matrix Template
               </p>
               <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Historical data indicates a 2.4% variance in seasonal travel times.dispatch engine currently applying winter offset.
               </p>
            </InfoCard>

            <MetricCard
               label="Efficiency Rating"
               value="A+"
               icon={Activity}
               iconColor="text-emerald-500"
               subValue="98th Percentile"
            />
          </div>
        </div>
      </DetailContentTemplate>
    </DashboardPageTemplate>
  );
}
