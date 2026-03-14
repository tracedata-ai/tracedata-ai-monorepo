"use client";

import { useEffect, useState } from "react";
import { StatCard } from "@/components/shared/StatCard";
import { ActivityIcon, TrendingUpIcon, AlertTriangleIcon } from "lucide-react";
import { entitiesApi } from "@/lib/api";
import { cn } from "@/lib/utils";

/**
 * Fleet Overview (Dashboard Home)
 *
 * Provides a high-level summary of the entire fleet's operational health,
 * including active vehicles, system availability, and urgent alerts.
 */
export default function Home() {
  const [stats, setStats] = useState({
    fleetCount: 0,
    activeTrips: 0,
    alertCount: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        setLoading(true);
        const [fleet, trips, issues] = await Promise.all([
          entitiesApi.getFleet(),
          entitiesApi.getTrips(),
          entitiesApi.getIssues(),
        ]);
        
        setStats({
          fleetCount: fleet.total,
          activeTrips: trips.items.filter(t => t.status === "ongoing").length,
          alertCount: issues.items.filter(i => i.status === "open").length,
        });
      } catch (err) {
        console.error("Failed to load dashboard stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Overview</h2>
        <p className="text-slate-500">
          Monitor your fleet activity and statistics here.
        </p>
      </div>

      {/* High-Level Analytics Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <StatCard
          title="Total Fleet"
          value={loading ? "..." : stats.fleetCount.toString()}
          icon={ActivityIcon}
          iconClassName="text-slate-400"
          className="hover:border-slate-300"
        />

        <StatCard
          title="Active Missions"
          value={loading ? "..." : stats.activeTrips.toString()}
          icon={TrendingUpIcon}
          iconClassName="text-slate-400"
          className="hover:border-slate-300"
        />

        <StatCard
          title="Urgent Alerts"
          value={loading ? "..." : stats.alertCount.toString()}
          icon={AlertTriangleIcon}
          iconClassName={stats.alertCount > 0 ? "text-red-400" : "text-slate-400"}
          valueClassName={stats.alertCount > 0 ? "text-red-600" : "text-slate-900"}
          className={cn(
            "hover:border-slate-300",
            stats.alertCount > 0 && "border-t-2 border-t-red-500"
          )}
        />
      </div>
    </div>
  );
}
