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
  History
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
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl shadow-2xl backdrop-blur-xl">
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
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden">
      {/* Breadcrumb Header */}
      <header className="bg-white dark:bg-slate-900 border-b border-border px-8 py-5 flex-shrink-0">
        <nav className="flex items-center text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          <Link href="/dashboard/drivers" className="hover:text-brand-blue hover:bg-brand-blue/5 px-2 py-1 rounded transition-colors flex items-center gap-1.5 -ml-2">
            <ArrowLeft className="w-4 h-4" />
            Drivers Hub
          </Link>
          <ChevronRight className="w-4 h-4 mx-3" />
          <span className="text-foreground">{driver.id}</span>
        </nav>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-4 sm:p-8 bg-slate-50/50 dark:bg-slate-900/50">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
            <div className="flex items-center gap-5">
              <div className="w-16 h-16 rounded-full bg-brand-blue/10 flex items-center justify-center text-brand-blue font-bold text-2xl shadow-sm border border-brand-blue/20">
                {driver.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h1 className="text-3xl font-black text-foreground tracking-tight">{driver.name}</h1>
                <p className="text-brand-blue font-bold mt-1 font-mono">{driver.id}</p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-sm font-bold uppercase border shadow-sm ${
                 driver.status === "Active"
                 ? "bg-brand-teal/10 text-brand-teal border-brand-teal/20"
                 : driver.status === "On Break" 
                 ? "bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 border-amber-200 dark:border-amber-800/50"
                 : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-700"
             }`}>
              {driver.status === "Active" && <div className="w-2 h-2 rounded-full bg-brand-teal animate-pulse"></div>}
              {driver.status === "On Break" && <div className="w-2 h-2 rounded-full bg-amber-500"></div>}
              {driver.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
             <div className="col-span-1 lg:col-span-2 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <div className="flex justify-between items-center mb-8">
                     <h3 className="text-sm font-bold text-foreground uppercase tracking-widest flex items-center gap-2">
                       <TrendingUp className="w-4 h-4 text-brand-blue" />
                       Performance Trajectory
                     </h3>
                     <div className="flex gap-2">
                        <span className="flex items-center gap-1.5 text-[10px] font-bold text-muted-foreground uppercase">
                          <div className="w-2 h-2 rounded-full bg-brand-teal"></div> Trip Scores
                        </span>
                     </div>
                   </div>

                   <div className="h-[300px] w-full">
                     <ResponsiveContainer width="100%" height="100%">
                       <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                         <defs>
                           <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                             <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
                             <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                           </linearGradient>
                         </defs>
                         <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(203, 213, 225, 0.2)" />
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
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 sm:p-8 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <Activity className="w-4 h-4 text-brand-blue" />
                     Aggregate Performance metrics
                   </h3>
                   
                   <div className="grid grid-cols-2 gap-6">
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-xl border border-border">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Trips Completed</p>
                         <p className="text-3xl font-black text-foreground mt-2 font-mono flex items-baseline gap-2">
                           {driver.tripsCompleted}
                           <span className="text-sm text-green-500 font-bold uppercase tracking-wider flex items-center">
                             +12% <span className="text-xs text-muted-foreground ml-1">vs avg</span>
                           </span>
                         </p>
                      </div>
                      
                      <div className="bg-slate-50 dark:bg-slate-800/50 p-5 rounded-xl border border-border">
                         <p className="text-xs text-slate-500 uppercase font-bold tracking-widest">Customer Rating</p>
                         <p className="text-3xl font-black text-foreground mt-2 flex items-center gap-2">
                           {driver.rating.toFixed(1)}
                           <Award className="w-6 h-6 text-amber-500" />
                         </p>
                      </div>

                      <div className="col-span-2 bg-gradient-to-br from-brand-teal/5 to-transparent dark:from-brand-teal/10 p-6 rounded-xl border border-brand-teal/20">
                        <div className="flex justify-between items-center mb-2">
                           <p className="text-xs text-brand-teal uppercase font-bold tracking-widest">Aggregate Trip Score</p>
                           <p className="text-3xl font-black text-brand-teal">{driver.avgTripScore}</p>
                        </div>
                        <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mb-2">
                           <div className="bg-brand-teal h-2 rounded-full" style={{ width: `${driver.avgTripScore}%` }}></div>
                        </div>
                        <p className="text-xs text-muted-foreground font-medium">Derived from telemetry, routing efficiency, and customer sentiment.</p>
                      </div>
                   </div>
                </div>

                {driver.explanation && (
                  <div className="glass-card p-6 sm:p-8 rounded-2xl relative overflow-hidden group">
                    {/* Decorative Motif */}
                    <div className="absolute right-0 top-0 w-32 h-32 text-brand-blue/10 transform translate-x-10 -translate-y-10 group-hover:scale-110 transition-transform">
                      <BrainCircuit className="w-full h-full" />
                    </div>

                    <h3 className="text-sm font-bold text-foreground mb-8 uppercase tracking-widest flex items-center gap-2 relative z-10">
                      <div className="p-1.5 bg-purple-500/10 rounded-lg">
                        <BrainCircuit className="w-4 h-4 text-purple-500" />
                      </div>
                      Behavioral DNA (Enhanced XAI)
                    </h3>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-10 relative z-10">
                      <div className="space-y-6">
                        <div>
                          <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest mb-4">AI Personality Narrative</p>
                          <blockquote className="text-lg font-medium text-foreground text-balance leading-relaxed border-l-4 border-purple-500/30 pl-6 py-1 italic">
                            "{driver.explanation.humanSummary}"
                          </blockquote>
                        </div>
                        <div className="flex gap-4">
                          <div className="px-3 py-1.5 bg-brand-teal/10 rounded-lg border border-brand-teal/20">
                            <p className="text-[8px] text-brand-teal uppercase font-bold tracking-tighter">Fairness Score</p>
                            <p className="text-sm font-bold font-mono text-brand-teal">{driver.explanation.fairnessAuditScore.toFixed(3)}</p>
                          </div>
                          <div className="px-3 py-1.5 bg-purple-500/10 rounded-lg border border-purple-500/20">
                            <p className="text-[8px] text-purple-500 uppercase font-bold tracking-tighter">Confidence</p>
                            <p className="text-sm font-bold font-mono text-purple-500">High</p>
                          </div>
                        </div>
                      </div>

                      <div className="space-y-5">
                        <p className="text-[10px] text-muted-foreground uppercase font-bold tracking-widest">Feature Contribution Profile</p>
                        <div className="space-y-4">
                          {Object.entries(driver.explanation.featureImportance).map(([feature, value], idx) => (
                            <div key={feature} className="space-y-2 animate-in fade-in slide-in-from-left duration-500" style={{ animationDelay: `${idx * 80}ms` }}>
                              <div className="flex justify-between items-end">
                                <span className="text-[9px] font-bold text-slate-500 uppercase tracking-wide font-mono px-2 py-0.5 bg-slate-100 dark:bg-slate-800 rounded">
                                  {feature.replace('_', ' ')}
                                </span>
                                <span className={`text-[10px] font-black font-mono ${value >= 0 ? 'text-brand-teal' : 'text-rose-500'}`}>
                                  {value >= 0 ? 'SIGNIFICANT' : 'OPTIMIZABLE'} ({ (value * 100).toFixed(1)}%)
                                </span>
                              </div>
                              <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex shadow-inner">
                                <div 
                                  className={`h-full rounded-full transition-all duration-1000 ease-out shadow-sm ${value >= 0 ? 'bg-gradient-to-r from-brand-teal to-brand-blue' : 'bg-gradient-to-r from-rose-500 to-orange-400'}`}
                                  style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                    
                    <div className="mt-8 pt-6 border-t border-border flex justify-between items-center text-[10px] text-muted-foreground font-bold uppercase tracking-widest">
                      <span>Last Analysis: 5 mins ago</span>
                      <button className="text-brand-blue hover:underline">Download Detailed SHAP Report</button>
                    </div>
                  </div>
                )}
             </div>

             <div className="col-span-1 space-y-6">
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <History className="w-4 h-4 text-brand-blue" />
                     Recent Journey Log
                   </h3>
                   <div className="space-y-4">
                      {driver.tripHistory.slice(-5).reverse().map((trip) => (
                        <div key={trip.tripId} className="flex justify-between items-center p-3 rounded-lg border border-border bg-slate-50/50 dark:bg-slate-800/30">
                           <div className="space-y-1">
                              <p className="text-xs font-bold text-foreground font-mono">{trip.tripId}</p>
                              <p className="text-[9px] text-muted-foreground font-bold uppercase tracking-tighter">
                                {new Date(trip.date).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                              </p>
                           </div>
                           <div className={`px-2 py-1 rounded text-xs font-black font-mono ${
                              trip.score >= 90 ? 'text-brand-teal bg-brand-teal/10' :
                              trip.score >= 80 ? 'text-brand-blue bg-brand-blue/10' :
                              'text-rose-500 bg-rose-500/10'
                           }`}>
                              {trip.score}
                           </div>
                        </div>
                      ))}
                   </div>
                   <button className="w-full mt-4 py-2 text-[10px] font-bold text-muted-foreground uppercase tracking-widest border border-dashed border-border rounded hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
                      View All 14 Trips
                   </button>
                </div>

                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-border shadow-sm">
                   <h3 className="text-sm font-bold text-foreground mb-6 uppercase tracking-widest flex items-center gap-2">
                     <ShieldAlert className="w-4 h-4 text-amber-500" />
                     Compliance
                   </h3>
                   
                   <div className="space-y-6">
                      <div>
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-1 mb-2">
                           <FileCheck2 className="w-3 h-3" /> License Status
                         </p>
                         <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-bold border ${
                            driver.licenseStatus === "Valid" ? "bg-green-5 text-green-700 border-green-200 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400" :
                            driver.licenseStatus === "Expiring Soon" ? "bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-400" :
                            "bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400"
                         }`}>
                            {driver.licenseStatus}
                         </div>
                      </div>
                      
                      <div className="pt-4 border-t border-border">
                         <p className="text-[10px] text-slate-500 uppercase font-bold tracking-widest flex items-center gap-1 mb-2">
                           <AlertTriangle className="w-3 h-3" /> Recent Incidents
                         </p>
                         {driver.recentIncidents === 0 ? (
                           <div className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded border border-border">
                             <p className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                               <UserCheck className="w-4 h-4 text-green-500" /> Clean record for past 30 days.
                             </p>
                           </div>
                         ) : (
                           <div className="bg-red-50 dark:bg-red-900/10 p-3 rounded border border-red-200 dark:border-red-800/50">
                             <p className="text-xl font-bold text-red-600 dark:text-red-400 font-mono mb-1">{driver.recentIncidents}</p>
                             <p className="text-xs font-bold text-red-800/60 dark:text-red-300">Incidents logged this period.</p>
                           </div>
                         )}
                      </div>
                   </div>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
