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
  BrainCircuit,
  ShieldAlert,
  Activity,
  Zap,
  TrendingDown,
  TrendingUp,
  Target
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
  ReferenceLine,
  Scatter,
  ComposedChart
} from "recharts";

interface TelemetryPoint { timestamp: string; speed: number; dynamics: number; rewardType?: string }
interface TooltipProps { active?: boolean; payload?: { payload: TelemetryPoint }[] }
const CustomTelemetryTooltip = ({ active, payload }: TooltipProps) => {
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
                 {(data.dynamics as number) > 0 ? <TrendingUp className="w-3 h-3 text-emerald-500" /> : (data.dynamics as number) < 0 ? <TrendingDown className="w-3 h-3 text-rose-500" /> : null}
                 <span className={cn("text-sm font-bold font-mono", (data.dynamics as number) > 0 ? 'text-emerald-500' : (data.dynamics as number) < 0 ? 'text-rose-500' : 'text-slate-400')}>
                    {(data.dynamics as number).toFixed(0)}%
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

const RewardPoint = (props: Record<string, unknown>) => {
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

  const telemetryData = trip.telemetrySegments?.map(seg => ({
    ...seg,
    dynamics: seg.throttlePos - (seg.brakePressure * 1.5)
  }));

  const formatMinsToHours = (mins: number) => {
    const hours = Math.floor(mins / 60);
    const remainingMins = mins % 60;
    return hours > 0 
      ? remainingMins > 0 ? `${hours}h ${remainingMins}m` : `${hours}h`
      : `${remainingMins}m`;
  };

  return (
    <DashboardPageTemplate
      title={trip.id}
      description={`Real-time manifest entry analysis • ${trip.routeId}`}
      breadcrumbs={
        <>
          <Link href="/dashboard/trips" className="hover:text-brand-blue transition-colors flex items-center gap-1.5">
            <ArrowLeft className="w-3 h-3" />
            Manifest
          </Link>
          <ChevronRight className="w-3 h-3 mx-2 opacity-30" />
          <span className="text-slate-900">{trip.id}</span>
        </>
      }
      headerActions={
        <>
          <Button variant="outline" size="sm">Export Packet</Button>
          <Button size="sm">Live Feed</Button>
        </>
      }
    >
      <DetailContentTemplate
        heroIcon={Route}
        heroTitle={trip.id}
        heroSubtitle={`Route ID: ${trip.routeId}`}
        highlights={[
          {
            label: "Current Status",
            value: trip.status,
            className: cn(
              trip.status === "In Progress" ? "text-brand-blue" :
              trip.status === "Completed" ? "text-emerald-600" :
              "text-slate-500"
            )
          },
          {
            label: "Completion",
            value: `${Math.round(((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)}%`,
            icon: Target,
            iconColor: "text-brand-blue"
          }
        ]}
      >
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <div className="lg:col-span-3 space-y-8">
            <FeatureCard
              title="Telemetric Dynamics Overlay"
              icon={Activity}
            >
               <div className="flex gap-6 mt-4 mb-8">
                  <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                     <div className="w-3 h-1.5 rounded-full bg-brand-blue"></div> Speed (km/h)
                  </div>
                  <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                     <div className="w-3 h-1.5 rounded-full bg-rose-400"></div> Dynamics (%)
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
                    <p className="text-xs text-slate-400 font-bold uppercase tracking-widest italic font-mono">Telemetry link inactive</p>
                 </div>
               )}
            </FeatureCard>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
               <InfoCard
                  title="Asset Links"
                  icon={Car}
                  items={[
                    { 
                      label: "Assigned Driver", 
                      value: (
                        <Link href={`/dashboard/drivers/${trip.driverId}`} className="text-brand-blue font-bold hover:underline">
                          {trip.driverId}
                        </Link>
                      )
                    },
                    { label: "Active Vehicle", value: trip.vehicleId, className: "font-mono" }
                  ]}
               />

               <MetricCard
                  label="Temporal Statistics"
                  value={trip.actualDurationMins ? formatMinsToHours(trip.actualDurationMins) : 'Active'}
                  subValue={`Baseline: ${formatMinsToHours(trip.historicalAvgMins)}`}
                  icon={Clock}
               />
            </div>

            {trip.explanation && (
              <FeatureCard
                title="Decision Forensic Deep-Pass"
                icon={BrainCircuit}
                variant="brand"
                isNarrative
              >
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                  <div className="lg:col-span-1 space-y-8">
                     <div className="bg-slate-50/50 border border-slate-100 p-8 rounded-3xl">
                        <p className="text-xs text-slate-400 uppercase font-black tracking-widest mb-4">Identity Narrative</p>
                        <p className="text-xl font-medium text-slate-900 leading-tight italic">
                          &ldquo;{trip.explanation.humanSummary}&rdquo;
                        </p>
                     </div>

                     <div className="bg-slate-900 text-white p-8 rounded-3xl space-y-6 shadow-xl">
                       <div className="flex items-center gap-3 text-emerald-400">
                         <ShieldCheck className="w-5 h-5 font-bold" />
                         <p className="text-xs font-bold uppercase tracking-widest">Fairness Audit</p>
                       </div>
                       <div className="flex justify-between items-end">
                          <p className="text-[10px] text-slate-500 uppercase font-bold">Statistical Parity Score</p>
                          <p className="text-3xl font-mono font-bold text-emerald-400 leading-none">{trip.explanation.fairnessAuditScore.toFixed(3)}</p>
                       </div>
                       <Progress value={trip.explanation.fairnessAuditScore * 100} className="h-1.5 bg-slate-800" />
                     </div>
                  </div>

                  <div className="lg:col-span-2 space-y-10">
                     <p className="text-xs text-brand-blue uppercase font-bold tracking-[0.2em] border-b border-slate-100 pb-6">
                       Feature Influence Vectors (SHAP)
                     </p>
                     <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-10">
                        {Object.entries(trip.explanation.featureImportance).map(([feature, value]) => (
                          <div key={feature} className="space-y-3">
                             <div className="flex justify-between items-center text-[10px] font-bold font-mono">
                               <span className="text-slate-500 uppercase tracking-widest">
                                 {feature.replace('_', ' ')}
                               </span>
                               <span className={cn((value as number) >= 0 ? 'text-emerald-500' : 'text-rose-500')}>
                                 {(value as number) >= 0 ? '+' : ''}{ ((value as number) * 100).toFixed(1) }%
                               </span>
                             </div>
                             <Progress 
                                value={Math.abs(value as number) * 100} 
                                className={cn(
                                  "h-1.5 transition-all duration-1000",
                                  (value as number) >= 0 ? "[&>div]:bg-emerald-500" : "[&>div]:bg-rose-500"
                                )}
                                style={{ marginLeft: (value as number) >= 0 ? '0' : 'auto', width: '100% ' }}
                             />
                          </div>
                        ))}
                     </div>
                  </div>
                </div>
              </FeatureCard>
            )}
          </div>

          <div className="space-y-8">
            <FeatureCard title="Validation Registry" icon={ShieldCheck}>
               {trip.status === "Completed" && trip.score !== undefined ? (
                  <div className="flex flex-col items-center justify-center py-6 text-center">
                     <div className="relative mb-8">
                        <svg className="w-32 h-32 transform -rotate-90">
                           <circle cx="64" cy="64" r="58" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-100" />
                           <circle cx="64" cy="64" r="58" stroke="#14b8a6" strokeWidth="8" fill="transparent" strokeDasharray={364.4} strokeDashoffset={364.4 - (364.4 * trip.score) / 100} strokeLinecap="round" className="transition-all duration-1000 ease-out" />
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                           <span className="text-4xl font-black text-slate-900 font-mono">{trip.score}</span>
                        </div>
                     </div>
                     <div className="bg-emerald-50 text-emerald-600 px-4 py-1.5 rounded-full flex items-center gap-2 mb-4 border border-emerald-100">
                        <Zap className="w-3.5 h-3.5 fill-current" />
                        <span className="text-[10px] font-bold uppercase tracking-wider">Reward Activated</span>
                     </div>
                     <p className="text-[10px] text-slate-400 font-bold uppercase tracking-tight">
                       Behavior verified by agent
                     </p>
                  </div>
               ) : (
                  <div className="flex flex-col items-center justify-center py-10 text-center opacity-30">
                     <ShieldCheck className="w-8 h-8 text-slate-400 mb-2" />
                     <p className="text-[10px] font-bold uppercase tracking-widest">Pending Closure</p>
                  </div>
               )}
            </FeatureCard>

            <InfoCard
              title="Tracked Odometer"
              icon={MapPin}
              items={[
                { label: "Completion", value: `${Math.round(((trip.currentDistanceKm || 0) / trip.distanceKm) * 100)}%` },
                { 
                  label: "Raw Odo", 
                  value: `${trip.currentDistanceKm?.toFixed(1) || 0} / ${trip.distanceKm.toFixed(1)} km`,
                  className: "col-span-2 font-mono" 
                }
              ]}
            >
              <Progress value={((trip.currentDistanceKm || 0) / trip.distanceKm) * 100} className="h-2 mt-6" />
            </InfoCard>

            <MetricCard
              label="Safety Index"
              value="100"
              icon={ShieldAlert}
              iconColor="text-emerald-500"
              subValue="Zero Incidents"
            />
          </div>
        </div>
      </DetailContentTemplate>
    </DashboardPageTemplate>
  );
}
