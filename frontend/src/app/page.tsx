import { StatCard } from "@/components/shared/StatCard";
import { ActivityIcon, TrendingUpIcon, AlertTriangleIcon } from "lucide-react";

/**
 * Fleet Overview (Dashboard Home)
 *
 * Provides a high-level summary of the entire fleet's operational health,
 * including active vehicles, system availability, and urgent alerts.
 */
export default function Home() {
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
          title="Active Vehicles"
          value="98"
          icon={ActivityIcon}
          iconClassName="text-slate-400"
          className="hover:border-slate-300"
        />

        <StatCard
          title="Deployment Rate"
          value="92.4%"
          icon={TrendingUpIcon}
          iconClassName="text-slate-400"
          className="hover:border-slate-300"
        />

        <StatCard
          title="System Alerts"
          value="3"
          icon={AlertTriangleIcon}
          iconClassName="text-red-400"
          valueClassName="text-slate-900"
          className="hover:border-slate-300 border-t-2 border-t-red-500"
        />
      </div>
    </div>
  );
}
