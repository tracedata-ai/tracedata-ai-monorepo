import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  LayoutDashboardIcon,
  ActivityIcon,
  TrendingUpIcon,
  AlertTriangleIcon,
} from "lucide-react";

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
        {/* Active Deployment Card */}
        <Card className="border shadow-none transition-all hover:border-slate-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold">
              Active Vehicles
            </CardTitle>
            <ActivityIcon className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">98</div>
          </CardContent>
        </Card>

        {/* Operational Efficiency Card */}
        <Card className="border shadow-none transition-all hover:border-slate-300">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold">
              Deployment Rate
            </CardTitle>
            <TrendingUpIcon className="h-4 w-4 text-slate-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">92.4%</div>
          </CardContent>
        </Card>

        {/* Urgent Monitoring Card */}
        <Card className="border shadow-none transition-all hover:border-slate-300 border-t-2 border-t-red-500">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold">
              System Alerts
            </CardTitle>
            <AlertTriangleIcon className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">3</div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
