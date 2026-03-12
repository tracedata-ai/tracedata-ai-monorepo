"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig, TripHistoryEntry } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  UserCheck,
  ShieldAlert,
  Award,
  Activity,
  BrainCircuit,
  TrendingUp,
  History,
  ShieldCheck,
  Zap,
  User
} from "lucide-react";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { MetricCard } from "@/components/shared/MetricCard";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white/90 border border-slate-200 p-4 rounded-xl shadow-xl backdrop-blur-md">
        <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-1">{label}</p>
        <p className="text-xl font-black text-brand-teal font-mono">
          Score: {payload[0].value}
        </p>
        <p className="text-[10px] text-slate-500 font-bold mt-2 uppercase">Trip ID: {payload[0].payload.tripId}</p>
      </div>
    );
  }
  return null;
};

export default function DriverDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const driverId = resolvedParams.id;
  
  const driver = dashboardConfig.drivers.find((d) => d.id === driverId);
  
  if (!driver) {
    notFound();
  }

  const chartData = driver.tripHistory.map((entry: TripHistoryEntry) => ({
    date: new Date(entry.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    score: entry.score,
    tripId: entry.tripId,
    fullDate: entry.date
  }));

  return (
    <DashboardPageTemplate
      title={driver.name}
      description={`AI-Inferred Behavior Profile for ${driver.id}`}
      breadcrumbs={
        <>
          <Link href="/dashboard/drivers" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-3 h-3" />
            Drivers Hub
          </Link>
          <ChevronRight className="w-3 h-3 mx-2 opacity-30" />
          <span className="text-slate-900">{driver.id}</span>
        </>
      }
      headerActions={
        <Button variant="outline" size="sm">
          Export Profile
        </Button>
      }
    >
      <DetailContentTemplate
        heroIcon={User}
        heroTitle={driver.name}
        heroSubtitle={driver.id}
        highlights={[
          {
            label: "Current Status",
            value: driver.status,
            className: cn(
              driver.status === 'Active' ? 'text-emerald-600' :
              driver.status === 'On Break' ? 'text-amber-500' :
              'text-slate-400'
            )
          },
          {
            label: "Avg. Score",
            value: driver.avgTripScore,
            icon: Award,
            iconColor: "text-emerald-500"
          }
        ]}
      >
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <FeatureCard 
              title="Performance Trajectory" 
              icon={TrendingUp}
            >
               <div className="h-[300px] w-full mt-4">
                 <ResponsiveContainer width="100%" height="100%">
                   <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                     <defs>
                       <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                         <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.1}/>
                         <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                       </linearGradient>
                     </defs>
                     <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(203, 213, 225, 0.3)" />
                     <XAxis 
                        dataKey="date" 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }} 
                        dy={10}
                     />
                     <YAxis 
                        domain={[0, 100]} 
                        axisLine={false} 
                        tickLine={false} 
                        tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                     />
                     <Tooltip content={<CustomTooltip />} />
                     <Area 
                        type="monotone" 
                        dataKey="score" 
                        stroke="#14b8a6" 
                        strokeWidth={3}
                        fillOpacity={1} 
                        fill="url(#colorScore)" 
                        animationDuration={1500}
                     />
                   </AreaChart>
                 </ResponsiveContainer>
               </div>
            </FeatureCard>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
               <MetricCard
                  label="Trips Completed"
                  value={driver.tripsCompleted}
                  icon={Activity}
                  trend={{ value: 12, label: "vs baseline", isPositive: true }}
               />
               <MetricCard
                  label="Customer Rating"
                  value={driver.rating.toFixed(1)}
                  icon={Award}
                  iconColor="text-amber-500"
                  subValue="Top 5% of fleet"
               />
            </div>

            {driver.explanation && (
              <FeatureCard
                title="Behavioral DNA"
                icon={BrainCircuit}
                variant="brand"
                isNarrative
              >
                <div className="space-y-6">
                  <div className="text-xl font-medium text-slate-900 leading-relaxed italic border-l-4 border-brand-blue/20 pl-6 py-1">
                    "{driver.explanation.humanSummary}"
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-slate-100">
                    <div className="space-y-6">
                      <p className="text-xs text-brand-blue uppercase font-bold tracking-widest">Feature Contribution Profile</p>
                      <div className="space-y-5">
                        {Object.entries(driver.explanation.featureImportance).map(([feature, value]) => (
                          <div key={feature} className="space-y-2">
                            <div className="flex justify-between items-end text-xs font-bold font-mono">
                               <span className="text-slate-500 uppercase tracking-tight">{feature.replace('_', ' ')}</span>
                               <span className={cn((value as number) >= 0 ? 'text-emerald-500' : 'text-rose-500')}>
                                 {(value as number) >= 0 ? '+' : ''}{((value as number) * 100).toFixed(1)}%
                               </span>
                            </div>
                            <Progress 
                              value={Math.abs(value as number) * 100} 
                              className={cn(
                                "h-1.5 transition-all duration-1000",
                                (value as number) >= 0 ? "[&>div]:bg-emerald-500" : "[&>div]:bg-rose-500"
                              )}
                              style={{ marginLeft: (value as number) >= 0 ? '0' : 'auto', width: '100%' }}
                            />
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="flex flex-col justify-center gap-6 bg-slate-50/50 p-8 rounded-3xl border border-slate-100">
                      <div className="space-y-2">
                        <p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Model Fairness Score</p>
                        <p className="text-3xl font-black font-mono text-brand-teal">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
                        <p className="text-xs text-emerald-500 font-bold uppercase tracking-tight flex items-center gap-2">
                           <ShieldCheck className="w-4 h-4" /> Bias-Free Certified
                        </p>
                      </div>
                      <div className="pt-6 border-t border-slate-200">
                        <p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Prediction Confidence</p>
                        <div className="flex items-center gap-3 mt-2">
                          <Zap className="w-5 h-5 text-amber-500 fill-amber-500" />
                          <span className="text-lg font-black text-slate-900">HIGH</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </FeatureCard>
            )}
          </div>

          <div className="space-y-8">
            <FeatureCard title="Journey Log" icon={History}>
              <div className="space-y-3 mt-4">
                {driver.tripHistory.slice(-5).reverse().map((trip) => (
                  <div key={trip.tripId} className="flex justify-between items-center p-4 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-brand-blue/5 transition-colors group">
                     <div className="space-y-1">
                        <p className="text-sm font-bold text-slate-900 font-mono tracking-tight group-hover:text-brand-blue">{trip.tripId}</p>
                        <p className="text-[10px] text-slate-400 font-bold uppercase tracking-[0.1em]">
                          {new Date(trip.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                        </p>
                     </div>
                     <div className={cn(
                        "px-3 py-1 rounded-full text-xs font-bold font-mono tracking-tighter border",
                        trip.score >= 90 ? 'text-emerald-600 bg-emerald-50 border-emerald-100' :
                        trip.score >= 80 ? 'text-brand-blue bg-brand-blue/10 border-brand-blue/20' :
                        'text-rose-500 bg-rose-50 border-rose-100'
                     )}>
                        {trip.score}
                     </div>
                  </div>
                ))}
              </div>
            </FeatureCard>

            <InfoCard
              title="Compliance Audit"
              icon={ShieldAlert}
              items={[
                { 
                  label: "License Status", 
                  value: (
                    <span className={cn(
                      "px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest border",
                      driver.licenseStatus === "Valid" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
                      driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-100" :
                      "bg-rose-50 text-rose-600 border-rose-100"
                    )}>
                      {driver.licenseStatus}
                    </span>
                  )
                },
                {
                  label: "Safety Record (30d)",
                  value: driver.recentIncidents === 0 ? "No Incidents" : `${driver.recentIncidents} Events`,
                  className: driver.recentIncidents > 0 ? "text-rose-600" : "text-emerald-600"
                }
              ]}
            />
          </div>
        </div>
      </DetailContentTemplate>
    </DashboardPageTemplate>
  );
}
