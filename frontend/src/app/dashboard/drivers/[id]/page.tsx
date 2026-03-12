"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig, TripHistoryEntry } from "@/config/dashboard";
import { GlassCard } from "@/components/shared/GlassCard";
import { MetricCard } from "@/components/shared/MetricCard";
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
  Zap
} from "lucide-react";
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
      {/* Breadcrumb Header */}
      <header className="bg-white border-b border-slate-100 px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
          <Link href="/dashboard/drivers" className="hover:text-brand-blue transition-colors flex items-center gap-1.5 -ml-2 px-2 py-1 rounded-full hover:bg-slate-50">
            <ArrowLeft className="w-3.5 h-3.5" />
            Drivers Hub
          </Link>
          <ChevronRight className="w-3.5 h-3.5 mx-3 opacity-30" />
          <span className="text-slate-900">{driver.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="flex items-center gap-6">
              <div className="w-16 h-16 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue font-black text-2xl border border-brand-blue/10 shadow-sm">
                {driver.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h1 className="text-4xl font-black text-slate-900 tracking-tighter">{driver.name}</h1>
                <p className="text-brand-blue font-black mt-1 uppercase tracking-widest text-xs">{driver.id}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-[10px] font-black uppercase tracking-widest shadow-sm ${
                 driver.status === "Active"
                 ? "bg-emerald-50 text-emerald-600 border border-emerald-100"
                 : driver.status === "On Break" 
                 ? "bg-amber-50 text-amber-700 border border-amber-100"
                 : "bg-slate-50 text-slate-500 border border-slate-200"
             }`}>
              {driver.status === "Active" && <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>}
              {driver.status === "On Break" && <div className="w-2 h-2 rounded-full bg-amber-500"></div>}
              {driver.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <GlassCard className="relative overflow-hidden">
                   <div className="flex justify-between items-center mb-10 relative z-10">
                     <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] flex items-center gap-2">
                       <TrendingUp className="w-4 h-4 text-brand-blue" />
                       Performance Trajectory
                     </h3>
                     <div className="flex gap-2">
                        <span className="flex items-center gap-1.5 text-[10px] font-black text-slate-400 uppercase tracking-tighter">
                          <div className="w-2 h-1 rounded-full bg-brand-teal"></div> Trip Scores
                        </span>
                     </div>
                   </div>

                   <div className="h-[300px] w-full">
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
                            tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 800 }} 
                            dy={10}
                         />
                         <YAxis 
                            domain={[0, 100]} 
                            axisLine={false} 
                            tickLine={false} 
                            tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 800 }}
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
                </GlassCard>

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
                       <div className="w-full bg-slate-100 rounded-full h-1.5 mb-2">
                          <div className="bg-brand-teal h-1.5 rounded-full" style={{ width: `${driver.avgTripScore}%` }}></div>
                       </div>
                       <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">Derived from telemetry, routing efficiency, and customer sentiment.</p>
                   </MetricCard>
                </div>

                {driver.explanation && (
                  <GlassCard className="relative overflow-hidden group">
                    <div className="absolute right-0 top-0 w-32 h-32 text-brand-blue/[0.03] transform translate-x-10 -translate-y-10 group-hover:scale-110 transition-transform">
                      <BrainCircuit className="w-full h-full" />
                    </div>

                    <h3 className="text-[10px] font-black text-slate-400 mb-8 uppercase tracking-[0.2em] flex items-center gap-3">
                      <div className="p-2 bg-slate-50 rounded-xl text-slate-900 border border-slate-100">
                        <BrainCircuit className="w-4 h-4" />
                      </div>
                      Behavioral DNA (XAI Forensic)
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-12 relative z-10">
                      <div className="space-y-8">
                        <div className="bg-slate-50/50 border border-slate-100 p-8 rounded-3xl">
                          <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-4">AI Personality Narrative</p>
                          <blockquote className="text-xl font-bold text-slate-900 leading-tight italic">
                            "{driver.explanation.humanSummary}"
                          </blockquote>
                        </div>
                        <div className="flex gap-4">
                          <div className="px-4 py-2 bg-brand-teal/5 rounded-2xl border border-brand-teal/10">
                            <p className="text-[9px] text-brand-teal uppercase font-black tracking-widest">Fairness Audit</p>
                            <p className="text-sm font-black font-mono text-brand-teal">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
                          </div>
                          <div className="px-4 py-2 bg-brand-blue/5 rounded-2xl border border-brand-blue/10">
                            <p className="text-[9px] text-brand-blue uppercase font-black tracking-widest">Confidence</p>
                            <p className="text-sm font-black font-mono text-brand-blue">High</p>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-6">
                        <p className="text-[10px] text-slate-400 uppercase font-black tracking-[0.2em] border-b border-slate-50 pb-6">Feature Contribution Profile</p>
                        <div className="space-y-5">
                          {Object.entries(driver.explanation.featureImportance).map(([feature, value], idx) => (
                            <div key={feature} className="space-y-2">
                              <div className="flex justify-between items-end">
                                <span className="text-[9px] font-black text-slate-900 uppercase tracking-widest">
                                  {feature.replace('_', ' ')}
                                </span>
                                <span className={`text-[10px] font-black font-mono ${value >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                  {value >= 0 ? '+' : ''}{ (value * 100).toFixed(1)}%
                                </span>
                              </div>
                              <div className="h-1 w-full bg-slate-100 rounded-full overflow-hidden flex">
                                <div 
                                  className={`h-full rounded-full transition-all duration-1000 ease-out ${value >= 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                                  style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </GlassCard>
                )}
             </div>

             <div className="col-span-1 space-y-6">
                <GlassCard>
                   <h3 className="text-[10px] font-black text-slate-400 mb-8 uppercase tracking-widest flex items-center gap-2">
                     <History className="w-4 h-4 text-brand-blue" />
                     Journey Log
                   </h3>
                   <div className="space-y-3">
                      {driver.tripHistory.slice(-5).reverse().map((trip) => (
                        <div key={trip.tripId} className="flex justify-between items-center p-4 rounded-2xl border border-slate-100 bg-slate-50/50 hover:bg-brand-blue/5 transition-colors group">
                           <div className="space-y-1">
                              <p className="text-[10px] font-black text-slate-900 font-mono tracking-tighter group-hover:text-brand-blue">{trip.tripId}</p>
                              <p className="text-[9px] text-slate-400 font-bold uppercase tracking-tighter">
                                {new Date(trip.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                              </p>
                           </div>
                           <div className={`px-3 py-1 rounded-full text-[10px] font-black font-mono tracking-tighter ${
                              trip.score >= 90 ? 'text-emerald-600 bg-emerald-50' :
                              trip.score >= 80 ? 'text-brand-blue bg-brand-blue/10' :
                              'text-rose-500 bg-rose-50'
                           }`}>
                              {trip.score}
                           </div>
                        </div>
                      ))}
                   </div>
                </GlassCard>

                <GlassCard>
                   <h3 className="text-[10px] font-black text-slate-400 mb-8 uppercase tracking-widest flex items-center gap-2">
                     <ShieldAlert className="w-4 h-4 text-amber-500" />
                     Compliance Audit
                   </h3>
                   
                   <div className="space-y-8">
                      <div>
                         <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-4">License Status</p>
                         <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-2xl text-[10px] font-black uppercase tracking-widest border ${
                            driver.licenseStatus === "Valid" ? "bg-emerald-50 text-emerald-600 border-emerald-100" :
                            driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-100" :
                            "bg-rose-50 text-rose-600 border-rose-100"
                         }`}>
                            {driver.licenseStatus}
                         </div>
                      </div>
                      
                      <div className="pt-6 border-t border-slate-50">
                         <p className="text-[10px] text-slate-400 uppercase font-black tracking-widest mb-4">Safety Record (30d)</p>
                         {driver.recentIncidents === 0 ? (
                           <div className="bg-emerald-50/50 border border-emerald-100 p-6 rounded-3xl">
                             <p className="text-[10px] text-emerald-600 font-black uppercase tracking-tight flex items-center gap-2">
                               <ShieldCheck className="w-4 h-4" /> Perfect Period Verified
                             </p>
                           </div>
                         ) : (
                           <div className="bg-rose-50 border border-rose-100 p-6 rounded-3xl flex items-center gap-6">
                              <p className="text-4xl font-black text-rose-600 font-mono leading-none">{driver.recentIncidents}</p>
                              <p className="text-[10px] font-black text-rose-700/60 uppercase tracking-tighter leading-tight">Detected Risk<br/>Events Logged</p>
                           </div>
                         )}
                      </div>
                   </div>
                </GlassCard>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
