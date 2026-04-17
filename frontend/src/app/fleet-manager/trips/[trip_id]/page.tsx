"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getTripDetail, type TripDetail } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, MapPin, Shield, Brain, MessageSquare, Smile } from "lucide-react";
import {
  Chart as ChartJS,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from "chart.js";
import { Doughnut, Bar } from "react-chartjs-2";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend);

// ── helpers ──────────────────────────────────────────────────────────────────

const statusClass: Record<string, string> = {
  active: "bg-blue-500",
  completed: "bg-green-600",
  zombie: "bg-gray-500",
};

const severityClass: Record<string, string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
};

const priorityClass: Record<string, string> = {
  high: "bg-red-600",
  normal: "bg-slate-500",
  low: "bg-blue-500",
};

function LV({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
        {label}
      </span>
      <span className="text-sm font-medium">{value ?? "—"}</span>
    </div>
  );
}

// ── Score Gauge ───────────────────────────────────────────────────────────────

function ScoreGauge({ score }: { score: number }) {
  const pct = Math.min(100, Math.max(0, score * 10));
  const color =
    score >= 8 ? "#22c55e" : score >= 5 ? "#eab308" : "#ef4444";
  const remaining = 100 - pct;

  const data = {
    datasets: [
      {
        data: [pct, remaining],
        backgroundColor: [color, "rgba(255,255,255,0.05)"],
        borderWidth: 0,
        circumference: 220,
        rotation: -110,
      },
    ],
  };

  return (
    <div className="relative flex flex-col items-center justify-center">
      <div style={{ width: 180, height: 130, position: "relative" }}>
        <Doughnut
          data={data}
          options={{ cutout: "75%", plugins: { legend: { display: false }, tooltip: { enabled: false } } }}
        />
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-2">
          <span className="text-3xl font-bold" style={{ color }}>
            {score.toFixed(1)}
          </span>
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground">
            / 10
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Score breakdown horizontal bars ──────────────────────────────────────────

function ScoreBreakdown({ breakdown }: { breakdown: Record<string, number> }) {
  const labels = Object.keys(breakdown).map((k) =>
    k.replace(/_component$/, "").replace(/_/g, " ")
  );
  const values = Object.values(breakdown);
  const max = Math.max(...values, 1);

  return (
    <div className="space-y-3">
      {labels.map((label, i) => {
        const pct = (values[i] / max) * 100;
        const color = pct > 66 ? "#ef4444" : pct > 33 ? "#eab308" : "#22c55e";
        return (
          <div key={label} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="capitalize text-muted-foreground">{label}</span>
              <span className="font-semibold" style={{ color }}>
                {values[i].toFixed(1)}
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-white/10">
              <div
                className="h-2 rounded-full transition-all"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
          </div>
        );
      })}
      <p className="pt-1 text-[10px] text-muted-foreground">
        Higher bar = greater contribution to risk score
      </p>
    </div>
  );
}

// ── Emotion radar (horizontal bars) ──────────────────────────────────────────

function EmotionBars({ emotions }: { emotions: Record<string, number> }) {
  const emotionColors: Record<string, string> = {
    fatigue: "#f97316",
    anxiety: "#a855f7",
    anger: "#ef4444",
    sadness: "#3b82f6",
  };

  return (
    <div className="space-y-3">
      {Object.entries(emotions).map(([key, val]) => {
        const pct = Math.round(val * 100);
        const color = emotionColors[key] ?? "#6b7280";
        return (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="capitalize text-muted-foreground">{key}</span>
              <span className="font-semibold" style={{ color }}>
                {pct}%
              </span>
            </div>
            <div className="h-2 w-full rounded-full bg-white/10">
              <div
                className="h-2 rounded-full"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Event dot map (static SVG placeholder with lat/lon markers) ──────────────

function EventDotMap({
  events,
}: {
  events: TripDetail["safety_events"];
}) {
  const withCoords = events.filter((e) => e.lat != null && e.lon != null);
  if (withCoords.length === 0) return null;

  const lats = withCoords.map((e) => e.lat!);
  const lons = withCoords.map((e) => e.lon!);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLon = Math.min(...lons);
  const maxLon = Math.max(...lons);
  const latRange = maxLat - minLat || 0.01;
  const lonRange = maxLon - minLon || 0.01;

  const W = 600;
  const H = 200;
  const PAD = 30;

  const toX = (lon: number) =>
    PAD + ((lon - minLon) / lonRange) * (W - 2 * PAD);
  const toY = (lat: number) =>
    H - PAD - ((lat - minLat) / latRange) * (H - 2 * PAD);

  const sevColor: Record<string, string> = {
    critical: "#dc2626",
    high: "#f97316",
    medium: "#eab308",
    low: "#3b82f6",
  };

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="w-full rounded-xl border border-white/10 bg-white/5"
      style={{ maxHeight: 200 }}
    >
      {/* grid */}
      {[0.25, 0.5, 0.75].map((f) => (
        <line
          key={f}
          x1={PAD}
          y1={H * f}
          x2={W - PAD}
          y2={H * f}
          stroke="rgba(255,255,255,0.05)"
          strokeWidth={1}
        />
      ))}
      {/* event dots */}
      {withCoords.map((e, i) => {
        const cx = toX(e.lon!);
        const cy = toY(e.lat!);
        const color = sevColor[e.severity?.toLowerCase()] ?? "#9ca3af";
        return (
          <g key={e.event_id}>
            <circle cx={cx} cy={cy} r={8} fill={color} opacity={0.85} />
            <text
              x={cx}
              y={cy + 4}
              textAnchor="middle"
              fontSize={9}
              fill="white"
              fontWeight="bold"
            >
              {i + 1}
            </text>
          </g>
        );
      })}
      {/* legend */}
      <text x={PAD} y={H - 8} fontSize={9} fill="rgba(255,255,255,0.4)">
        Relative event positions (lat/lon projected)
      </text>
    </svg>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function TripDetailPage() {
  const params = useParams();
  const router = useRouter();
  const tripId = params.trip_id as string;

  const [detail, setDetail] = useState<TripDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    getTripDetail(tripId)
      .then(setDetail)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [tripId]);

  if (loading) {
    return (
      <div className="p-8 space-y-4 max-w-5xl mx-auto">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-40 w-full" />)}
        </div>
        <Skeleton className="h-48 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (notFound || !detail) {
    return (
      <div className="p-8 flex flex-col items-center gap-4 text-center">
        <p className="text-muted-foreground">Trip not found.</p>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
      </div>
    );
  }

  const score = detail.scoring.score;
  const breakdown = detail.scoring.breakdown;
  const hasBreakdown = Object.keys(breakdown).length > 0;
  const criticalEvents = detail.safety_events.filter(
    (e) => e.severity?.toLowerCase() === "critical"
  ).length;
  const escalated = detail.safety_events.filter(
    (e) => e.decision?.toLowerCase() === "escalate"
  ).length;

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* ── Header ── */}
      <div className="flex flex-wrap items-start gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back
        </Button>
        <div className="flex-1 min-w-0">
          <h1 className="text-xl font-semibold truncate">
            {detail.route_name ?? "Trip"} — {detail.driver_name ?? "Unknown Driver"}
          </h1>
          <p className="text-xs text-muted-foreground font-mono mt-0.5">{detail.trip_id}</p>
        </div>
        <Badge className={`${statusClass[detail.status] ?? "bg-gray-500"} text-white capitalize`}>
          {detail.status}
        </Badge>
      </div>

      {/* ── Trip metadata ── */}
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle className="text-sm">Trip Overview</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <LV label="Driver" value={detail.driver_name} />
          <LV label="Vehicle" value={detail.license_plate ?? detail.vehicle} />
          <LV label="Route" value={detail.route_name} />
          <LV
            label="Distance"
            value={detail.distance_km ? `${detail.distance_km} km` : null}
          />
          <LV label="From" value={detail.route_from} />
          <LV label="To" value={detail.route_to} />
          <LV
            label="Started"
            value={detail.created_at ? new Date(detail.created_at).toLocaleString() : null}
          />
          <LV label="Safety Events" value={detail.safety_events.length.toString()} />
        </CardContent>
      </Card>

      {/* ── Score + breakdown ── */}
      {score != null && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="glass rounded-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Brain className="h-4 w-4 text-purple-400" /> Safety Score
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-3">
              <ScoreGauge score={score} />
              <p className="text-xs text-center text-muted-foreground px-2">
                {score >= 8
                  ? "Good — driver performance within acceptable bounds."
                  : score >= 5
                  ? "Fair — coaching recommended to address identified patterns."
                  : "Poor — immediate intervention advised."}
              </p>
            </CardContent>
          </Card>

          {hasBreakdown && (
            <Card className="glass rounded-xl">
              <CardHeader>
                <CardTitle className="text-sm">Score Breakdown (XAI)</CardTitle>
              </CardHeader>
              <CardContent>
                <ScoreBreakdown breakdown={breakdown} />
              </CardContent>
            </Card>
          )}
        </div>
      )}

      {/* ── XAI narrative ── */}
      {detail.scoring.narrative && (
        <Card className="glass rounded-xl border border-purple-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Brain className="h-4 w-4 text-purple-400" /> Explainability Narrative
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-muted-foreground rounded-lg bg-white/5 px-4 py-3">
              {detail.scoring.narrative}
            </p>
            <p className="mt-2 text-[10px] text-muted-foreground">
              Generated by the Scoring Agent using heuristic decomposition.
              Score components reflect jerk, speed, lateral force, and engine load signals.
            </p>
          </CardContent>
        </Card>
      )}

      {/* ── Safety events ── */}
      {detail.safety_events.length > 0 && (
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Shield className="h-4 w-4 text-orange-400" /> Safety Events
              <span className="ml-auto flex gap-2">
                {criticalEvents > 0 && (
                  <Badge className="bg-red-600 text-white text-[10px]">
                    {criticalEvents} Critical
                  </Badge>
                )}
                {escalated > 0 && (
                  <Badge className="bg-orange-500 text-white text-[10px]">
                    {escalated} Escalated
                  </Badge>
                )}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <EventDotMap events={detail.safety_events} />
            <div className="space-y-3 mt-2">
              {detail.safety_events.map((e, i) => (
                <div
                  key={e.event_id}
                  className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-muted-foreground font-mono">#{i + 1}</span>
                    <span className="text-sm font-medium capitalize">
                      {e.event_type.replace(/_/g, " ")}
                    </span>
                    <Badge
                      className={`${severityClass[e.severity?.toLowerCase()] ?? "bg-gray-500"} text-white text-[10px] capitalize`}
                    >
                      {e.severity}
                    </Badge>
                    {e.decision && (
                      <Badge
                        className={`${e.decision === "escalate" ? "bg-red-600" : "bg-yellow-600"} text-white text-[10px] capitalize`}
                      >
                        {e.decision}
                      </Badge>
                    )}
                    {e.timestamp && (
                      <span className="ml-auto text-[10px] text-muted-foreground">
                        {new Date(e.timestamp).toLocaleTimeString()}
                      </span>
                    )}
                  </div>
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs text-muted-foreground">
                    {e.lat != null && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {e.lat.toFixed(4)}, {e.lon?.toFixed(4)}
                      </span>
                    )}
                    {e.traffic && <span>Traffic: {e.traffic}</span>}
                    {e.weather && <span>Weather: {e.weather}</span>}
                    {e.action && <span>Action: {e.action}</span>}
                  </div>
                  {e.reason && (
                    <p className="text-xs rounded bg-white/5 px-3 py-2 text-muted-foreground">
                      {e.reason}
                    </p>
                  )}
                  {e.recommended_action && (
                    <p className="text-xs text-blue-300">
                      Recommended: {e.recommended_action}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ── Sentiment ── */}
      {detail.sentiment && (
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Smile className="h-4 w-4 text-yellow-400" /> Driver Sentiment
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div className="flex flex-col items-center justify-center gap-2">
              <div
                className="text-4xl font-bold"
                style={{
                  color:
                    detail.sentiment.label === "positive"
                      ? "#22c55e"
                      : detail.sentiment.label === "negative"
                      ? "#ef4444"
                      : "#eab308",
                }}
              >
                {detail.sentiment.score != null
                  ? `${Math.round(detail.sentiment.score * 100)}%`
                  : "—"}
              </div>
              <Badge
                className={`capitalize ${
                  detail.sentiment.label === "positive"
                    ? "bg-green-600"
                    : detail.sentiment.label === "negative"
                    ? "bg-red-600"
                    : "bg-yellow-600"
                } text-white`}
              >
                {detail.sentiment.label ?? "Unknown"}
              </Badge>
              <p className="text-xs text-muted-foreground text-center">
                Analysed from post-trip driver feedback
              </p>
            </div>
            {Object.keys(detail.sentiment.emotions).length > 0 && (
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                  Emotion Signals
                </p>
                <EmotionBars emotions={detail.sentiment.emotions} />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── Coaching ── */}
      {detail.coaching.length > 0 && (
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <MessageSquare className="h-4 w-4 text-green-400" /> Coaching Messages
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {detail.coaching.map((c, i) => (
              <div
                key={i}
                className="rounded-xl border border-white/10 bg-white/5 p-4 space-y-2"
              >
                <div className="flex items-center gap-2">
                  <Badge
                    className={`${priorityClass[c.priority] ?? "bg-gray-500"} text-white text-[10px] capitalize`}
                  >
                    {c.priority}
                  </Badge>
                  <span className="text-xs text-muted-foreground capitalize">
                    {c.category.replace(/_/g, " ")}
                  </span>
                </div>
                <p className="text-sm leading-relaxed">{c.message}</p>
              </div>
            ))}

            {/* Bias / fairness note */}
            <div className="rounded-xl border border-blue-500/20 bg-blue-500/5 p-4 mt-2">
              <p className="text-xs font-semibold text-blue-300 mb-1">Fairness & Bias Mitigation</p>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Coaching messages are generated with AIF360 fairness correction applied.
                Driver experience level is used as the protected attribute — scores and
                coaching are adjusted to prevent systematic bias against junior or senior drivers.
                This trip was evaluated under the{" "}
                <span className="text-blue-300">equalised odds</span> constraint.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
