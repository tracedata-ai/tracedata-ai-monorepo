"use client";

import { use } from "react";
import Link from "next/link";
import { notFound } from "next/navigation";
import { dashboardConfig } from "@/config/dashboard";
import {
  ChevronRight,
  ArrowLeft,
  Route,
  Clock,
  ShieldCheck,
  MapPin,
  Car,
  Scale,
  BrainCircuit,
  ShieldAlert,
  Activity,
  Zap,
  CheckCircle2,
  TrendingDown,
  TrendingUp,
  Target
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
  ReferenceLine,
  Scatter,
  ScatterChart,
  ComposedChart,
  ZAxis
} from "recharts";

const CustomTelemetryTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white/90 border border-slate-200 p-4 rounded-xl shadow-xl backdrop-blur-md">
        <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-2 font-mono">{data.timestamp}</p>
        <div className="space-y-1.5">
           <div className="flex justify-between items-center gap-6">
              <span className="text-xs font-bold text-slate-500 uppercase">Speed</span>
              <span className="text-sm font-bold text-brand-blue font-mono">{data.speed} km/h</span>
           </div>
           <div className="flex justify-between items-center gap-6">
              <span className="text-xs font-bold text-slate-500 uppercase">Dynamics</span>
              <div className="flex items-center gap-1.5">
                 {data.dynamics > 0 ? <TrendingUp className="w-3 h-3 text-emerald-500" /> : data.dynamics < 0 ? <TrendingDown className="w-3 h-3 text-rose-500" /> : null}
                 <span className={`text-sm font-bold font-mono ${data.dynamics > 0 ? 'text-emerald-500' : data.dynamics < 0 ? 'text-rose-500' : 'text-slate-400'}`}>
                    {data.dynamics.toFixed(0)}%
                 </span>
              </div>
           </div>
        </div>
        {data.rewardType && (
          <div className="mt-3 pt-3 border-t border-slate-100 flex items-center gap-2 text-brand-teal">
             <div className="p-1 bg-brand-teal/10 rounded-full">
                <Zap className="w-3 h-3 fill-brand-teal" />
             </div>
             <span className="text-xs font-bold uppercase tracking-tight">Reward: {data.rewardType}</span>
          </div>
        )}
      </div>
    );
  }
  return null;
};

const RewardPoint = (props: any) => {
  const { cx, cy, payload } = props;
  if (payload.rewardType) {
    return (
      <svg x={cx - 10} y={cy - 10} width={20} height={20} viewBox="0 0 24 24" className="filter drop-shadow-sm">
        <circle cx="12" cy="12" r="8" fill="#14b8a6" fillOpacity="0.2" />
        <circle cx="12" cy="12" r="4" fill="#14b8a6" />
      </svg>
    );
  }
  return null;
};

export default function TripDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = use(params);
  const tripId = resolvedParams.id;
  
  const trip = dashboardConfig.trips.find((t) => t.id === tripId);
  
  if (!trip) {
    notFound();
  }

  // Pre-calculate dynamics line data: Accel - Brake
  const telemetryData = trip.telemetrySegments?.map(seg => ({
    ...seg,
    dynamics: seg.throttlePos - (seg.brakePressure * 1.5) // Weighted brake for clarity
  }));

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "In Progress": return "bg-brand-blue/5 text-brand-blue border border-brand-blue/10";
      case "Completed": return "bg-emerald-50 text-emerald-600 border border-emerald-100";
      case "Scheduled": return "bg-slate-50 text-slate-500 border border-slate-200";
      case "Cancelled": return "bg-rose-50 text-rose-600 border border-rose-100";
      default: return "";
    }
  };

  return (
    <div className="flex-1 flex flex-col min-w-0 bg-background h-full overflow-hidden text-slate-900">
      <header className="bg-white dark:bg-slate-900 border-b border-slate-100 flex-shrink-0">
        <DashboardSection gridCols={1} className="py-4">
          <nav className="flex items-center text-xs font-bold text-slate-400 uppercase tracking-widest">
            <Link href="/dashboard/trips" className="hover:text-brand-blue transition-colors flex items-center gap-1.5 -ml-2 px-2 py-1 rounded-full hover:bg-slate-50">
              <ArrowLeft className="w-3.5 h-3.5" />
              Manifest
            </Link>
            <ChevronRight className="w-3.5 h-3.5 mx-3 opacity-30" />
            <span className="text-slate-900 dark:text-slate-100">{trip.id}</span>
          </nav>
        </DashboardSection>
      </header>

      <div className="flex-1 overflow-auto bg-slate-50/30 dark:bg-slate-900/50">
        <DashboardSection gridCols={1} className="py-6">
          <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-6">
            <div className="flex items-center gap-6">
              <div className="w-14 h-14 rounded-2xl bg-brand-blue/5 flex items-center justify-center text-brand-blue border border-brand-blue/10">
                <Route className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-4xl font-black text-slate-900 dark:text-white tracking-tighter font-mono">{trip.id}</h1>
                <p className="text-slate-500 font-bold text-xs uppercase tracking-widest mt-1">
                  Ingested: {new Date(trip.startTime).toLocaleDateString()} at {new Date(trip.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                </p>
              </div>
            </div>
            
            <div className={`px-4 py-2 flex items-center gap-2 rounded-full text-xs font-bold uppercase tracking-widest shadow-sm border ${getStatusColor(trip.status)}`}>
              {trip.status === "In Progress" && <div className="w-2 h-2 rounded-full bg-brand-blue animate-pulse"></div>}
              {trip.status}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
             <div className="md:col-span-3 space-y-8">
                <FeatureCard
                  title="Telemetric Dynamics"
                  subtitle="Overlay: Speed vs. Pedal Pressure"
                  icon={Activity}
                >
                   <div className="flex gap-6 mt-4 mb-8">
                      <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-tight">
                         <div className="w-3 h-1 rounded-full bg-brand-blue"></div> Speed (km/h)
                      </div>
                      <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-tight">
                         <div className="w-3 h-1 rounded-full bg-rose-400"></div> Dynamics (±%)
                      </div>
                   </div>

                   {telemetryData ? (
                     <div className="h-[350px] w-full relative">
                       <ResponsiveContainer width="100%" height="100%">
                         <ComposedChart data={telemetryData} margin={{ top: 20, right: 10, left: -20, bottom: 0 }}>
                           <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(203, 213, 225, 0.3)" />
                           <XAxis 
                              dataKey="timestamp" 
                              axisLine={false} 
                              tickLine={false} 
                              tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }} 
                              dy={15}
                           />
                           <YAxis 
                              domain={[0, 100]} 
                              axisLine={false} 
                              tickLine={false} 
                              tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                           />
                           <Tooltip content={<CustomTelemetryTooltip />} cursor={{ stroke: '#f1f5f9', strokeWidth: 2 }} />
                           
                           {trip.nationalSpeedLimit && (
                             <ReferenceLine 
                                y={trip.nationalSpeedLimit} 
                                stroke="#94a3b8" 
                                strokeDasharray="5 5"
                                strokeWidth={1}
                                label={{ value: `Limit: ${trip.nationalSpeedLimit}`, position: 'right', fill: '#94a3b8', fontSize: 9, fontWeight: 700, dy: -10 }} 
                             />
                           )}

                           <Line 
                              type="monotone" 
                              dataKey="dynamics" 
                              stroke="#fb7185" 
                              strokeWidth={1.5} 
                              strokeOpacity={0.4}
                              dot={false}
                              activeDot={false}
                           />

                           <Line 
                              type="monotone" 
                              dataKey="speed" 
                              stroke="#3b82f6" 
                              strokeWidth={4} 
                              dot={false}
                              activeDot={{ r: 6, fill: '#3b82f6', stroke: '#fff', strokeWidth: 3 }}
                              animationDuration={1500}
                           />

                           <Scatter 
                              dataKey="speed" 
                              shape={<RewardPoint />}
                              animationDuration={2000}
                           />
                         </ComposedChart>
                       </ResponsiveContainer>
                     </div>
                   ) : (
                     <div className="h-[200px] flex items-center justify-center border-2 border-dashed border-slate-100 rounded-3xl mt-4">
                        <p className="text-xs text-slate-400 font-bold uppercase tracking-widest italic">Awaiting high-res telemetry packet...</p>
                     </div>
                   )}
                </FeatureCard>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                   <InfoCard
                      title="Asset Links"
                      icon={Car}
                      items={[
                        { 
                          label: "Driver", 
                          value: (
                            <Link href={`/dashboard/drivers/${trip.driverId}`} className="text-brand-blue font-bold hover:underline">
                              {trip.driverId}
                            </Link>
                          )
                        },
                        { label: "Vehicle", value: trip.vehicleId, className: "font-mono" }
                      ]}
                   />

                   <MetricCard
                      label="Temporal Metrics"
                      value={trip.actualDurationMins ? formatMinsToHours(trip.actualDurationMins) : '--'}
                      subValue={`Baseline: ${formatMinsToHours(trip.historicalAvgMins)}`}
                      icon={Clock}
                   />
                </div>

                {trip.explanation && (
                  <FeatureCard
                    title="Decision Forensic"
                    subtitle="AI Interpretability Layer"
                    icon={BrainCircuit}
                    variant="brand"
                    isNarrative
                  >
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                      <div className="lg:col-span-1 space-y-8">
                         <div className="bg-slate-50/50 dark:bg-slate-800/30 border border-slate-100 dark:border-slate-800 p-8 rounded-3xl">
                            <p className="text-xs text-slate-400 uppercase font-bold tracking-widest mb-4">AI Personality narrative</p>
                            <p className="text-xl font-medium text-slate-900 dark:text-slate-100 leading-tight italic">
                              "{trip.explanation.humanSummary}"
                            </p>
                         </div>

                         <div className="bg-slate-900 text-white p-8 rounded-3xl space-y-6 shadow-xl">
                           <div className="flex items-center gap-3 text-emerald-400">
                             <ShieldAlert className="w-5 h-5" />
                             <p className="text-xs font-bold uppercase tracking-widest">Fairness Audit</p>
                           </div>
                           <div className="flex justify-between items-end">
                              <p className="text-xs text-slate-400 uppercase font-bold">Statistical parity</p>
                              <p className="text-3xl font-mono font-bold text-emerald-400 leading-none">{trip.explanation.fairnessAuditScore.toFixed(3)}</p>
                           </div>
                           <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                              <div className="bg-emerald-400 h-full" style={{ width: `${(trip.explanation.fairnessAuditScore) * 100}%` }}></div>
                           </div>
                         </div>
                      </div>

                      <div className="lg:col-span-2 space-y-10">
                         <p className="text-xs text-brand-blue uppercase font-bold tracking-widest border-b border-slate-100 dark:border-slate-800 pb-6">
                           SHAP Influence Vector
                         </p>
                         <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-10">
                            {Object.entries(trip.explanation.featureImportance).map(([feature, value]) => (
                              <div key={feature} className="space-y-3">
                                 <div className="flex justify-between items-center text-xs font-bold">
                                   <span className="text-slate-500 uppercase tracking-widest">
                                     {feature.replace('_', ' ')}
                                   </span>
                                   <span className={value >= 0 ? 'text-emerald-500' : 'text-rose-500'}>
                                     {value >= 0 ? '+' : ''}{ (value * 100).toFixed(1) }%
                                   </span>
                                 </div>
                                 <div className="h-1.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden flex">
                                    <div 
                                      className={`h-full rounded-full transition-all duration-1000 ${value >= 0 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                                      style={{ width: `${Math.abs(value) * 100}%`, marginLeft: value >= 0 ? '0' : 'auto' }}
                                    ></div>
                                 </div>
                              </div>
                            ))}
                         </div>
                      </div>
                    </div>
                  </FeatureCard>
                )}
             </div>

             <div className="md:col-span-1 space-y-6">
                <FeatureCard 
                  title="Validation Hub" 
                  icon={ShieldCheck}
                >
                   {trip.status === "Completed" && trip.score !== undefined ? (
                      <div className="flex flex-col items-center justify-center py-6 text-center">
                         <div className="relative mb-8">
                            <svg className="w-32 h-32 transform -rotate-90">
                               <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-100 dark:text-slate-800" />
                               <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray={364.4} strokeDashoffset={364.4 - (364.4 * trip.score) / 100} className="text-emerald-500 transition-all duration-1000 ease-out" />
                            </svg>
                            <div className="absolute inset-0 flex items-center justify-center">
                               <span className="text-4xl font-black text-slate-900 dark:text-white font-mono">{trip.score}</span>
                            </div>
                         </div>
                         <div className="bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 px-4 py-2 rounded-full flex items-center gap-2 mb-4 border border-emerald-100 dark:border-emerald-800/30">
                            <Zap className="w-3.5 h-3.5 fill-current" />
                            <span className="text-xs font-bold uppercase tracking-wider">Reward Earned</span>
                         </div>
                         <p className="text-xs text-slate-500 font-medium leading-relaxed">
                           Behavior Agent verified optimal pedal modulation.
                         </p>
                      </div>
                   ) : (
                      <div className="flex flex-col items-center justify-center py-6 text-center opacity-40">
                         <div className="w-16 h-16 rounded-full border-2 border-dashed border-slate-300 flex items-center justify-center mb-4">
                           <ShieldCheck className="w-6 h-6 text-slate-400" />
                         </div>
                         <p className="text-[10px] font-bold uppercase text-slate-500">Awaiting Signal</p>
                      </div>
                   )}
                </FeatureCard>

                <InfoCard
                  title="Route Status"
                  icon={MapPin}
                  items={[
                    { label: "Completion", value: `${Math.round(((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)}%` },
                    { 
                      label: "Odometer", 
                      value: `${trip.currentDistanceKm?.toFixed(1) || 0} / ${trip.distanceKm.toFixed(1)} km`,
                      className: "col-span-2" 
                    }
                  ]}
                >
                  <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden mt-6">
                     <div className="h-full bg-brand-blue rounded-full transition-all duration-1000" style={{ width: `${((trip.currentDistanceKm || 0) / trip.distanceKm) * 100}%` }}></div>
                  </div>
                </InfoCard>
             </div>
          </div>
        </DashboardSection>
      </div>
    </div>
  );
}
