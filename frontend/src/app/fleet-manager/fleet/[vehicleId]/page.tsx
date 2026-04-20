"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { getVehicleDetail, type VehicleDetail } from "@/lib/api";
import { usePageAnimations } from "@/hooks/usePageAnimations";
import { Button } from "@/components/ui/button";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
);

const EVENT_TYPE_COLORS: Record<string, string> = {
  smoothness_log: "#8884d8",
  harsh_brake: "#ff7300",
  harsh_acceleration: "#ff0000",
  harsh_turn: "#ffbb28",
  speeding: "#ff69b4",
  collision: "#82ca9d",
  rollover: "#ffc658",
  end_of_trip: "#8dd1e1",
  start_of_trip: "#d084d0",
};

const SEV_COLOR: Record<string, string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
};

const DEC_COLOR: Record<string, string> = {
  escalate: "bg-red-600",
  monitor: "bg-yellow-600",
};

function scoreGrade(score: number): string {
  if (score >= 95) return "A+";
  if (score >= 90) return "A";
  if (score >= 85) return "A-";
  if (score >= 80) return "B+";
  if (score >= 75) return "B";
  if (score >= 70) return "B-";
  if (score >= 65) return "C+";
  if (score >= 60) return "C";
  if (score >= 57) return "D+";
  if (score >= 53) return "D";
  return "F";
}

function ScoreChip({ score }: { score: number | null }) {
  if (score === null) return <span className="text-muted-foreground text-xs">—</span>;
  const color = score >= 80 ? "text-green-600" : score >= 65 ? "text-amber-600" : "text-red-600";
  return (
    <span className={`font-mono font-semibold text-sm ${color}`}>
      {score} <span className="text-xs font-normal">({scoreGrade(score)})</span>
    </span>
  );
}

export default function VehicleDetailPage() {
  const params = useParams();
  const vehicleId = params?.vehicleId as string;
  const [detail, setDetail] = useState<VehicleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  usePageAnimations(containerRef, ".animate-card");

  useEffect(() => {
    if (!vehicleId) {
      setError("No vehicle ID provided");
      setLoading(false);
      return;
    }

    async function loadVehicleDetail() {
      try {
        const data = await getVehicleDetail(vehicleId);
        setDetail(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load vehicle details");
      } finally {
        setLoading(false);
      }
    }

    loadVehicleDetail();
  }, [vehicleId]);

  if (loading) {
    return (
      <div ref={containerRef}>
        <DashboardPageTemplate title="Vehicle Details" subtitle="Loading...">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <Skeleton key={i} className="h-64 w-full rounded-xl" />
            ))}
          </div>
        </DashboardPageTemplate>
      </div>
    );
  }

  if (error || !detail?.vehicle) {
    return (
      <div ref={containerRef}>
        <DashboardPageTemplate title="Vehicle Details" subtitle="Error">
          <Card className="glass rounded-xl">
            <CardContent className="pt-6">
              <div className="text-red-500">{error || "Vehicle not found"}</div>
              <Button onClick={() => router.back()} className="mt-4">
                Go Back
              </Button>
            </CardContent>
          </Card>
        </DashboardPageTemplate>
      </div>
    );
  }

  const { vehicle, statistics, trips, events_by_type } = detail;

  return (
    <div ref={containerRef}>
      <DashboardPageTemplate
        title={`${vehicle.model || "Unknown Model"} - ${vehicle.license_plate || "Unknown Plate"}`}
        subtitle={`Vehicle Details & Analytics`}
        stats={[
          { label: "Total Trips", value: statistics.total_trips.toString(), change: 1 },
          { label: "Unique Drivers", value: statistics.total_drivers.toString(), change: 1 },
          { label: "Avg Score", value: statistics.avg_score.toFixed(1), change: 1 },
          { label: "Status", value: vehicle.status || "unknown", change: 0 },
        ]}
      >
        <div className="flex flex-col gap-4">
          {/* Vehicle Overview */}
          <Card className="glass rounded-xl animate-card">
            <CardHeader>
              <CardTitle>Vehicle Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-400">Model</p>
                  <p className="text-lg font-semibold text-white">{vehicle.model || "Unknown"}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">License Plate</p>
                  <p className="text-lg font-semibold text-white">{vehicle.license_plate || "Unknown"}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Status</p>
                  <p className="text-lg font-semibold text-white capitalize">{vehicle.status || "unknown"}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-400">Fuel Level</p>
                  <p className="text-lg font-semibold text-white">{vehicle.fuel_level ?? 0}%</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Event Type Timeline - Smoothness Data */}
          {events_by_type.smoothness_log && events_by_type.smoothness_log.length > 0 && (
            <Card className="glass rounded-xl animate-card">
              <CardHeader>
                <CardTitle>Smoothness Profile Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                {(() => {
                  const smoothnessEvents = events_by_type.smoothness_log || [];
                  const labels = smoothnessEvents.map((_, idx) => `T${idx + 1}`);
                  const normalizeTo100 = (values: number[]) => {
                    const maxValue = Math.max(...values, 0);
                    if (maxValue <= 0) return values.map(() => 0);
                    return values.map((v) => Number(((v / maxValue) * 100).toFixed(2)));
                  };

                  const jerkRaw = smoothnessEvents.map((event) => {
                    const jerkMean = (event.details as any)?.jerk?.mean;
                    return jerkMean ? Number(jerkMean) : 0;
                  });
                  const lateralGRaw = smoothnessEvents.map((event) => {
                    const lateralG = (event.details as any)?.lateral?.mean_lateral_g;
                    return lateralG ? Number(lateralG) : 0;
                  });
                  const speedStdDevRaw = smoothnessEvents.map((event) => {
                    const speedStdDev = (event.details as any)?.speed?.std_dev;
                    return speedStdDev ? Number(speedStdDev) : 0;
                  });

                  const jerkData = normalizeTo100(jerkRaw);
                  const lateralGData = normalizeTo100(lateralGRaw);
                  const speedStdDevData = normalizeTo100(speedStdDevRaw);

                  const chartData = {
                    labels,
                    datasets: [
                      {
                        label: "Jerk Mean (normalized)",
                        data: jerkData,
                        borderColor: "#ff7300",
                        backgroundColor: "rgba(255, 115, 0, 0.1)",
                        tension: 0.3,
                      },
                      {
                        label: "Lateral G (normalized)",
                        data: lateralGData,
                        borderColor: "#ff69b4",
                        backgroundColor: "rgba(255, 105, 180, 0.1)",
                        tension: 0.3,
                      },
                      {
                        label: "Speed StdDev (normalized)",
                        data: speedStdDevData,
                        borderColor: "#82ca9d",
                        backgroundColor: "rgba(130, 202, 157, 0.1)",
                        tension: 0.3,
                      },
                    ],
                  };

                  return (
                    <div className="w-full h-80">
                      <Line
                        data={chartData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: { display: true },
                          },
                          scales: {
                            y: {
                              beginAtZero: true,
                              max: 100,
                            },
                          },
                        }}
                      />
                    </div>
                  );
                })()}
              </CardContent>
            </Card>
          )}

          {/* Harsh Events Distribution */}
          {(() => {
            const harshEventTypes = Object.keys(events_by_type).filter(
              (type) =>
                type.includes("harsh") ||
                type === "collision" ||
                type === "rollover" ||
                type === "speeding",
            );

            if (harshEventTypes.length === 0) return null;

            const labels = harshEventTypes.map((type) => type.replace(/_/g, " "));
            const data = harshEventTypes.map((type) => events_by_type[type]?.length || 0);
            const colors = harshEventTypes.map((type) => EVENT_TYPE_COLORS[type] || "#8884d8");

            const chartData = {
              labels,
              datasets: [
                {
                  label: "Event Count",
                  data,
                  backgroundColor: colors,
                  borderColor: colors,
                  borderWidth: 1,
                },
              ],
            };

            return (
              <Card className="glass rounded-xl animate-card">
                <CardHeader>
                  <CardTitle>Safety Events Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="w-full h-80">
                    <Bar
                      data={chartData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: { display: false },
                        },
                        scales: {
                          y: {
                            beginAtZero: true,
                          },
                        },
                      }}
                    />
                  </div>
                </CardContent>
              </Card>
            );
          })()}

          {/* Recent trips */}
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle>Recent Trips</CardTitle>
            </CardHeader>
            <CardContent>
              {trips.length === 0 ? (
                <p className="text-sm text-muted-foreground">No trips on record.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-muted/40">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Trip ID</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Route</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Status</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Score</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {trips
                      .slice()
                      .sort((a, b) => {
                        const aTime = a.created_at ? Date.parse(a.created_at) : 0;
                        const bTime = b.created_at ? Date.parse(b.created_at) : 0;
                        return bTime - aTime;
                      })
                      .map((trip) => (
                        <tr
                          key={trip.id}
                          onClick={() => router.push(`/fleet-manager/trips/${trip.id}`)}
                          className="cursor-pointer border-t border-border/50 hover:bg-muted/30 transition-colors"
                        >
                          <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">{trip.id.slice(0, 8)}</td>
                          <td className="px-4 py-2.5">{trip.route_name ?? "—"}</td>
                          <td className="px-4 py-2.5 capitalize">{trip.status}</td>
                          <td className="px-4 py-2.5"><ScoreChip score={trip.score} /></td>
                          <td className="px-4 py-2.5 text-xs text-muted-foreground">
                            {trip.created_at ? new Date(trip.created_at).toLocaleDateString() : "—"}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>

          {/* Safety events */}
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle>Safety Events</CardTitle>
            </CardHeader>
            <CardContent>
              {detail.safety_events.length === 0 ? (
                <p className="text-sm text-muted-foreground">No safety events on record.</p>
              ) : (
                <table className="w-full text-sm">
                  <thead className="bg-muted/40">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Event</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Severity</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Decision</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-muted-foreground">Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {detail.safety_events.map((event) => (
                      <tr
                        key={event.event_id}
                        onClick={() => router.push(`/fleet-manager/issues/${event.event_id}`)}
                        className="cursor-pointer border-t border-border/50 hover:bg-muted/30 transition-colors"
                      >
                        <td className="px-4 py-2.5 capitalize">{event.event_type.replace(/_/g, " ")}</td>
                        <td className="px-4 py-2.5">
                          <Badge className={`${SEV_COLOR[event.severity?.toLowerCase()] ?? "bg-gray-500"} text-white capitalize text-xs`}>
                            {event.severity}
                          </Badge>
                        </td>
                        <td className="px-4 py-2.5">
                          {event.decision
                            ? <Badge className={`${DEC_COLOR[event.decision.toLowerCase()] ?? "bg-gray-500"} text-white capitalize text-xs`}>{event.decision}</Badge>
                            : <span className="text-muted-foreground">—</span>}
                        </td>
                        <td className="px-4 py-2.5 text-xs text-muted-foreground">
                          {event.event_timestamp ? new Date(event.event_timestamp).toLocaleString() : "—"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </CardContent>
          </Card>
        </div>
      </DashboardPageTemplate>
    </div>
  );
}
