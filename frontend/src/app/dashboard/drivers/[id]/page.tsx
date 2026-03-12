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
  FileCheck2,
  AlertTriangle,
  BrainCircuit,
  TrendingUp,
  History,
  ShieldCheck,
  Zap,
  MapPin
} from "lucide-react";
import { InfoCard } from "@/components/shared/InfoCard";
import { FeatureCard } from "@/components/shared/FeatureCard";
import { DashboardSection } from "@/components/shared/DashboardSection";
import { MetricCard } from "@/components/shared/MetricCard";
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

  // Format data for Recharts
  const chartData = driver.tripHistory.map((entry: TripHistoryEntry) => ({
    date: new Date(entry.date).toLocaleDateString([], { month: 'short', day: 'numeric' }),
    score: entry.score,
    tripId: entry.tripId,
    fullDate: entry.date
  }));

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden text-slate-900">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-100 flex-shrink-0">
        <DashboardSection gridCols={1} className="py-4">
          <nav className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest">
            <Link href="/dashboard/drivers" className="hover:text-brand-blue transition-colors flex items-center gap-1.5 -ml-2 px-2 py-1 rounded-full hover:bg-slate-50">
              <ArrowLeft className="w-3.5 h-3.5" />
              Drivers Hub
            </Link>
            <ChevronRight className="w-3.5 h-3.5 mx-3 opacity-30" />
            <span className="text-slate-900 dark:text-slate-100">{driver.id}</span>
          </nav>
        </DashboardSection>
      </header>

      <div className="flex-1 overflow-auto bg-slate-50/30 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue font-black text-2xl border border-brand-blue/10 shadow-sm">
                {driver.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter">{driver.name}</h1>
                <p className="text-brand-blue font-bold mt-1 uppercase tracking-widest text-xs">{driver.id}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase tracking-widest shadow-sm border ${
                 driver.status === "Active"
                 ? "bg-emerald-50 text-emerald-600 border-emerald-100"
                 : driver.status === "On Break" 
                 ? "bg-amber-50 text-amber-700 border-amber-100"
                 : "bg-slate-50 text-slate-500 border-slate-200"
             }`}>
              {driver.status === "Active" && <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>}
              {driver.status === "On Break" && <div className="w-2 h-2 rounded-full bg-amber-500"></div>}
              {driver.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <FeatureCard 
                  title="Performance Trajectory" 
                  icon={TrendingUp}
                >
                   <div className="h-[250px] w-full mt-4">
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
                      trend={{
                        value: 12,
                        label: "vs baseline",
                        isPositive: true
                      }}
                   />
                   
                   <MetricCard
                      label="Customer Rating"
                      value={driver.rating.toFixed(1)}
                      icon={Award}
                      iconColor="text-amber-500"
                      subValue="Top 5% of fleet"
                   />

                   <MetricCard
                      label="Aggregate Trip Score"
                      value={driver.avgTripScore}
                      icon={BrainCircuit}
                      className="col-span-1 sm:col-span-2"
                   >
                       <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2 mt-4 mb-2">
                          <div className="bg-brand-teal h-full rounded-full transition-all duration-1000" style={{ width: `${driver.avgTripScore}%` }}></div>
                       </div>
                       <p className="text-xs text-slate-400 font-medium uppercase tracking-tight">Derived from telemetry, routing efficiency, and customer sentiment.</p>
                   </MetricCard>
                </div>

                {driver.explanation && (
                  <FeatureCard
                    title="Behavioral DNA"
                    subtitle="XAI Forensic Analysis"
                    icon={BrainCircuit}
                    variant="brand"
                    isNarrative
                  >
                    <div className="space-y-6">
                      <div className="text-xl font-medium text-slate-900 dark:text-slate-100 leading-relaxed italic border-l-4 border-brand-blue/20 pl-6 py-1">
                        "{driver.explanation.humanSummary}"
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-6 border-t border-slate-100 dark:border-slate-800">
                        <div className="space-y-6">
                          <p className="text-xs text-brand-blue uppercase font-bold tracking-widest">Feature Contribution Profile</p>
                          <div className="space-y-5">
                            {Object.entries(driver.explanation.featureImportance).map(([feature, value]) => (
                              <div key={feature} className="space-y-2">
                                <div className="flex justify-between items-end">
                                  <span className="text-xs font-bold text-slate-500 uppercase tracking-tight">
                                    {feature.replace('_', ' ')}
                                  </span>
                                  <span className={`text-xs font-bold font-mono ${value >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                    {value >= 0 ? '+' : ''}{ (value * 100).toFixed(1)}%
                                  </span>
                                </div>
                                <div className="h-1.5 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex">
                                  <div 
                                    className={`h-full rounded-full transition-all duration-1000 ease-out ${value >= 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                                    style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                                  ></div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div className="flex flex-col justify-center gap-6 bg-slate-50/50 dark:bg-slate-800/30 p-8 rounded-3xl border border-slate-100 dark:border-slate-800">
                          <div className="space-y-2">
                            <p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Model Fairness Score</p>
                            <p className="text-3xl font-black font-mono text-brand-teal">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
                            <p className="text-xs text-emerald-500 font-bold uppercase tracking-tight flex items-center gap-2">
                               <ShieldCheck className="w-4 h-4" /> Bias-Free Certified
                            </p>
                          </div>
                          <div className="pt-6 border-t border-slate-200 dark:border-slate-700">
                            <p className="text-xs text-slate-400 uppercase font-bold tracking-widest">Prediction Confidence</p>
                            <div className="flex items-center gap-3 mt-2">
                              <Zap className="w-5 h-5 text-amber-500 fill-amber-500" />
                              <span className="text-lg font-black text-slate-900 dark:text-slate-100">HIGH</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </FeatureCard>
                )}
             </div>

             <div className="col-span-1 space-y-6">
                <FeatureCard
                  title="Journey Log"
                  icon={History}
                >
                   <div className="space-y-3 mt-4">
                      {driver.tripHistory.slice(-5).reverse().map((trip) => (
                        <div key={trip.tripId} className="flex justify-between items-center p-4 rounded-2xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 hover:bg-brand-blue/5 transition-colors group">
                           <div className="space-y-1">
                              <p className="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono tracking-tight group-hover:text-brand-blue">{trip.tripId}</p>
                              <p className="text-xs text-slate-400 font-bold uppercase tracking-tight">
                                {new Date(trip.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                              </p>
                           </div>
                           <div className={`px-3 py-1 rounded-full text-xs font-bold font-mono tracking-tighter shadow-sm border ${
                              trip.score >= 90 ? 'text-emerald-600 bg-emerald-50 border-emerald-100' :
                              trip.score >= 80 ? 'text-brand-blue bg-brand-blue/10 border-brand-blue/20' :
                              'text-rose-500 bg-rose-50 border-rose-100'
                           }`}>
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
                >
                  {driver.recentIncidents === 0 ? (
                    <div className="mt-4 bg-emerald-50/50 dark:bg-emerald-900/10 border border-emerald-100 dark:border-emerald-800/20 p-4 rounded-2xl">
                      <p className="text-xs text-emerald-600 dark:text-emerald-500 font-bold uppercase tracking-tight flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4" /> Perfect Period Verified
                      </p>
                    </div>
                  ) : (
                    <div className="mt-4 bg-rose-50 dark:bg-rose-900/10 border border-rose-100 dark:border-rose-800/20 p-4 rounded-2xl flex items-center gap-4">
                      <AlertTriangle className="w-6 h-6 text-rose-500" />
                      <p className="text-xs font-bold text-rose-700/80 dark:text-rose-400 uppercase tracking-tight">
                        Risk events detected in current billing cycle.
                      </p>
                    </div>
                  )}
                </InfoCard>
             </div>
          </div>
        </DashboardSection>
      </div>
    </div>
  );
}
