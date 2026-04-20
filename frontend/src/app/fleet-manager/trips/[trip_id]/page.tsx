"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getTripDetail, type TripDetail } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, MapPin, Shield, Brain, MessageSquare, Smile, Star, CloudSun, Route, Eye } from "lucide-react";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler,
} from "chart.js";
import { Doughnut, Line } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
);

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

function ConditionChip({
  label,
  value,
  icon,
  tone = "neutral",
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
  tone?: "good" | "warn" | "bad" | "neutral";
}) {
  const toneClass: Record<string, string> = {
    good: "border-emerald-500/30 bg-emerald-500/10 text-emerald-300",
    warn: "border-amber-500/30 bg-amber-500/10 text-amber-300",
    bad: "border-rose-500/30 bg-rose-500/10 text-rose-300",
    neutral: "border-border bg-muted/40 text-cyan-300",
  };

  return (
    <div className={`flex items-center gap-3 rounded-xl border px-3 py-3 ${toneClass[tone]}`}>
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-900/70">
        {icon}
      </div>
      <div className="min-w-0">
        <p className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</p>
        <p className="truncate text-sm font-semibold text-foreground">{value}</p>
      </div>
    </div>
  );
}

function computeVisibility(weather: string | null, timestamp: string | null): string {
  const weatherText = (weather || "").toLowerCase();
  const hour = timestamp ? new Date(timestamp).getHours() : 12;

  if (weatherText.includes("rain") || weatherText.includes("storm") || weatherText.includes("fog")) {
    return "Low";
  }
  if (hour < 6 || hour >= 19) {
    return "Medium";
  }
  return "Good";
}

function getWeatherTone(weather: string): "good" | "warn" | "bad" | "neutral" {
  const text = weather.toLowerCase();
  if (text.includes("storm") || text.includes("thunder")) return "bad";
  if (text.includes("rain") || text.includes("fog") || text.includes("haze")) return "warn";
  if (text.includes("clear") || text.includes("sun")) return "good";
  return "neutral";
}

function getRoadTone(road: string): "good" | "warn" | "bad" | "neutral" {
  const text = road.toLowerCase();
  if (text.includes("severe") || text.includes("gridlock") || text.includes("heavy")) return "bad";
  if (text.includes("moderate") || text.includes("slow")) return "warn";
  if (text.includes("light") || text.includes("free") || text.includes("normal")) return "good";
  return "neutral";
}

function getVisibilityTone(visibility: string): "good" | "warn" | "bad" | "neutral" {
  const text = visibility.toLowerCase();
  if (text === "low") return "bad";
  if (text === "medium") return "warn";
  if (text === "good") return "good";
  return "neutral";
}

function weatherCodeToLabel(code: number): string {
  if (code === 0) return "Clear";
  if ([1, 2].includes(code)) return "Partly Cloudy";
  if (code === 3) return "Overcast";
  if ([45, 48].includes(code)) return "Fog";
  if ([51, 53, 55, 56, 57].includes(code)) return "Drizzle";
  if ([61, 63, 65, 66, 67, 80, 81, 82].includes(code)) return "Rain";
  if ([71, 73, 75, 77, 85, 86].includes(code)) return "Snow";
  if ([95, 96, 99].includes(code)) return "Thunderstorm";
  return "Weather Unavailable";
}

// ── Score Gauge ───────────────────────────────────────────────────────────────

function ScoreGauge({ score, label, gpa }: { score: number; label?: string | null; gpa?: number | null }) {
  const pct = Math.min(100, Math.max(0, score));
  const color = score >= 80 ? "#22c55e" : score >= 65 ? "#eab308" : "#ef4444";

  const data = {
    datasets: [
      {
        data: [pct, 100 - pct],
        backgroundColor: [color, "rgba(255,255,255,0.07)"],
        borderWidth: 0,
        circumference: 220,
        rotation: -110,
      },
    ],
  };

  return (
    <div className="flex flex-col items-center">
      {/* responsive:false + explicit w/h prevent canvas from collapsing */}
      <div className="relative" style={{ width: 180, height: 150 }}>
        <Doughnut
          data={data}
          width={180}
          height={150}
          options={{
            responsive: false,
            cutout: "74%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            animation: { duration: 700 },
          }}
        />
        {/* overlay sits in the doughnut hole — gauge opens at the bottom */}
        <div className="absolute inset-0 flex flex-col items-center justify-end pb-5">
          <span className="text-4xl font-bold tabular-nums" style={{ color }}>
            {score.toFixed(0)}
          </span>
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground leading-tight">
            / 100
          </span>
        </div>
      </div>
      {label && (
        <div className="flex items-center gap-2 mt-1">
          <span
            className="px-2 py-0.5 rounded-md text-sm font-semibold"
            style={{
              backgroundColor: score >= 80 ? "#16a34a22" : score >= 65 ? "#ca8a0422" : "#dc262622",
              color,
            }}
          >
            {label}
          </span>
          {gpa != null && (
            <span className="text-xs text-muted-foreground">{gpa.toFixed(1)} Grade</span>
          )}
        </div>
      )}
    </div>
  );
}

// ── Star rating (0–5 float) ───────────────────────────────────────────────────

function StarRating({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => {
        const fill = Math.min(1, Math.max(0, value - (star - 1)));
        return (
          <span key={star} className="relative inline-block text-amber-400" style={{ fontSize: "1.1rem" }}>
            <Star className="h-5 w-5 stroke-amber-400 fill-transparent" />
            {fill > 0 && (
              <span
                className="absolute inset-0 overflow-hidden"
                style={{ width: `${fill * 100}%` }}
              >
                <Star className="h-5 w-5 fill-amber-400 stroke-amber-400" />
              </span>
            )}
          </span>
        );
      })}
      <span className="ml-1.5 text-sm font-semibold tabular-nums text-amber-500">
        {value.toFixed(1)}
      </span>
      <span className="text-xs text-muted-foreground">/ 5</span>
    </div>
  );
}

// ── Score breakdown horizontal bars ──────────────────────────────────────────

function ScoreBreakdown({ breakdown }: { breakdown: Record<string, number> }) {
  const labelsByKey: Record<string, string> = {
    jerk_component: "Acceleration Smoothness",
    speed_component: "Speed Consistency",
    lateral_component: "Lateral Stability",
    engine_component: "Engine Load",
  };

  const labels = Object.keys(breakdown).map((k) =>
    labelsByKey[k] ?? k.replace(/_component$/, "").replace(/_/g, " ")
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
            <div className="h-2 w-full rounded-full bg-muted">
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

// ── F1-style smooth driving telemetry chart ─────────────────────────────────

function SmoothDrivingTelemetryChart({
  points,
}: {
  points: TripDetail["scoring"]["smoothness_points"];
}) {
  if (!points.length) return null;

  const labels = points.map((p, idx) => {
    if (!p.timestamp) return `P${idx + 1}`;
    return new Date(p.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  });

  const metricDefs = [
    { key: "jerk_mean", label: "Acceleration Smoothness", color: "#ef4444" },
    { key: "jerk_max", label: "Peak Acceleration Spike", color: "#f97316" },
    { key: "speed_std_dev", label: "Speed Variance", color: "#eab308" },
    { key: "mean_lateral_g", label: "Lateral G Mean", color: "#22c55e" },
    { key: "max_lateral_g", label: "Lateral G Max", color: "#06b6d4" },
    { key: "engine_load_avg", label: "Mean RPM", color: "#3b82f6" },
  ] as const;

  const datasets = metricDefs
    .map((metric) => {
      const series = points.map((p) => {
        const value = p[metric.key];
        return typeof value === "number" ? value : null;
      });
      const numericSeries = series.filter((v): v is number => typeof v === "number");
      if (!numericSeries.length) return null;
      const max = Math.max(...numericSeries, 1e-6);

      return {
        label: metric.label,
        data: series.map((v) => (typeof v === "number" ? Number(((v / max) * 100).toFixed(2)) : null)),
        borderColor: metric.color,
        backgroundColor: `${metric.color}33`,
        pointRadius: 2,
        pointHoverRadius: 4,
        borderWidth: 2,
        tension: 0.35,
      };
    })
    .filter((d): d is NonNullable<typeof d> => d !== null);

  if (!datasets.length) return null;

  return (
    <div className="rounded-xl border border-border bg-gradient-to-b from-slate-950/80 to-slate-900/60 p-3">
      <div className="relative h-72 w-full">
        <Line
          data={{ labels, datasets }}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: {
                  color: "#e2e8f0",
                  boxWidth: 10,
                  boxHeight: 10,
                  usePointStyle: true,
                },
              },
              tooltip: {
                backgroundColor: "rgba(15,23,42,0.92)",
                borderColor: "rgba(148,163,184,0.25)",
                borderWidth: 1,
                titleColor: "#f8fafc",
                bodyColor: "#e2e8f0",
              },
            },
            scales: {
              x: {
                ticks: { color: "#cbd5e1", maxRotation: 0, autoSkip: true, font: { size: 10 } },
                grid: { color: "rgba(148,163,184,0.12)" },
              },
              y: {
                min: 0,
                max: 100,
                ticks: { color: "#cbd5e1", callback: (v) => `${v}%` },
                grid: { color: "rgba(148,163,184,0.12)" },
              },
            },
          }}
        />
      </div>
      <p className="mt-2 text-[10px] text-slate-300">
        10-minute smooth driving pings (normalized per metric) for F1-style telemetry comparison.
      </p>
    </div>
  );
}

// ── Emotion bars ──────────────────────────────────────────────────────────────

function EmotionBars({ emotions }: { emotions: Record<string, number> }) {
  const emotionColors: Record<string, string> = {
    fatigue: "#f97316",
    anxiety: "#a855f7",
    anger: "#ef4444",
    sadness: "#3b82f6",
  };

  const entries = Object.entries(emotions);
  const allZero = entries.every(([, v]) => v === 0);

  if (allZero) {
    return (
      <p className="text-xs text-muted-foreground italic">
        No significant stress signals detected — driver feedback was predominantly calm and positive.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {entries.map(([key, val]) => {
        const pct = Math.round(val * 100);
        const color = emotionColors[key] ?? "#6b7280";
        return (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="capitalize text-muted-foreground">{key}</span>
              <span className="font-semibold" style={{ color }}>{pct}%</span>
            </div>
            <div className="h-2 w-full rounded-full bg-muted">
              <div
                className="h-2 rounded-full transition-all duration-500"
                style={{ width: `${pct}%`, backgroundColor: color }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ── Trip event map (Mapbox, multi-pin) ───────────────────────────────────────

const SEV_COLORS: Record<string, string> = {
  critical: "#dc2626",
  high: "#f97316",
  medium: "#eab308",
  low: "#3b82f6",
};

function TripEventMap({ events }: { events: TripDetail["safety_events"] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mapError, setMapError] = useState<string | null>(null);

  const withCoords = events.filter((e) => e.lat != null && e.lon != null);

  useEffect(() => {
    if (!withCoords.length) return;

    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token) {
      setMapError("NEXT_PUBLIC_MAPBOX_TOKEN is not set.");
      return;
    }

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let map: any = null;

    async function initMap() {
      try {
        const mapboxgl = (await import("mapbox-gl")).default;
        await import("mapbox-gl/dist/mapbox-gl.css");
        mapboxgl.accessToken = token!;

        if (!containerRef.current) return;

        map = new mapboxgl.Map({
          container: containerRef.current,
          style: "mapbox://styles/mapbox/streets-v12",
          center: [withCoords[0].lon!, withCoords[0].lat!],
          zoom: 12,
          minZoom: 9,
        });

        map.addControl(new mapboxgl.NavigationControl(), "top-right");
        map.addControl(new mapboxgl.FullscreenControl(), "top-right");

        withCoords.forEach((e, i) => {
          const color = SEV_COLORS[e.severity?.toLowerCase()] ?? "#9ca3af";

          const el = document.createElement("div");
          Object.assign(el.style, {
            width: "28px",
            height: "28px",
            borderRadius: "50%",
            background: color,
            color: "white",
            fontSize: "11px",
            fontWeight: "bold",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            border: "2px solid rgba(255,255,255,0.7)",
            cursor: "pointer",
            boxShadow: `0 0 8px ${color}88`,
          });
          el.textContent = String(i + 1);

          const popupHtml = `
            <div style="font-size:12px;color:#111;padding:4px 2px;line-height:1.5;">
              <strong>#${i + 1} — ${e.event_type.replace(/_/g, " ")}</strong><br/>
              ${e.location_name ? `<span style="color:#555">${e.location_name}</span><br/>` : ""}
              Severity: <strong>${e.severity}</strong><br/>
              ${e.decision ? `Decision: ${e.decision}<br/>` : ""}
              ${e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : ""}
            </div>`;

          new mapboxgl.Marker({ element: el })
            .setLngLat([e.lon!, e.lat!])
            .setPopup(new mapboxgl.Popup({ offset: 16 }).setHTML(popupHtml))
            .addTo(map);
        });

        if (withCoords.length > 1) {
          const bounds = new mapboxgl.LngLatBounds();
          withCoords.forEach((e) => bounds.extend([e.lon!, e.lat!]));
          map.fitBounds(bounds, { padding: 60, maxZoom: 14 });
        }
      } catch (err) {
        setMapError(String(err));
      }
    }

    initMap();
    return () => { map?.remove(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events.map((e) => e.event_id).join(",")]);

  if (!withCoords.length) return null;

  if (mapError) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl bg-muted/50 text-sm text-muted-foreground">
        <MapPin className="mr-2 h-4 w-4" /> Map unavailable: {mapError}
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="h-72 w-full rounded-xl overflow-hidden border border-border"
    />
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
  const [liveWeather, setLiveWeather] = useState<string | null>(null);

  useEffect(() => {
    getTripDetail(tripId)
      .then(setDetail)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [tripId]);

  useEffect(() => {
    async function hydrateWeatherFromCoords() {
      if (!detail) return;

      const latestConditionEvent = [...detail.safety_events]
        .reverse()
        .find((e) => e.weather || e.traffic || e.timestamp) || null;
      if (latestConditionEvent?.weather) return;

      const coordEvent = detail.safety_events.find((e) => e.lat != null && e.lon != null);
      if (coordEvent?.lat == null || coordEvent?.lon == null) return;

      try {
        const response = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${coordEvent.lat}&longitude=${coordEvent.lon}&current=weather_code&timezone=auto`
        );
        if (!response.ok) return;
        const payload = await response.json();
        const code = payload?.current?.weather_code;
        if (typeof code === "number") {
          setLiveWeather(weatherCodeToLabel(code));
        }
      } catch {
        setLiveWeather(null);
      }
    }

    hydrateWeatherFromCoords();
  }, [detail]);

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
  const scoreLabel = detail.scoring.score_label;
  const scoreGpa = detail.scoring.score_gpa;
  const driverScore = detail.scoring.driver_score;
  const breakdown = detail.scoring.breakdown;
  const hasBreakdown = Object.keys(breakdown).length > 0;
  const criticalEvents = detail.safety_events.filter(
    (e) => e.severity?.toLowerCase() === "critical"
  ).length;
  const escalated = detail.safety_events.filter(
    (e) => e.decision?.toLowerCase() === "escalate"
  ).length;
  const latestConditionEvent = [...detail.safety_events]
    .reverse()
    .find((e) => e.weather || e.traffic || e.timestamp) || null;
  const weatherCondition = latestConditionEvent?.weather || liveWeather || "Not Reported";
  const roadCondition = latestConditionEvent?.traffic || "Normal";
  const visibilityCondition = computeVisibility(
    latestConditionEvent?.weather ?? liveWeather ?? null,
    latestConditionEvent?.timestamp ?? detail.created_at
  );

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
      <Card className="rounded-xl">
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

      <Card className="rounded-xl">
        <CardHeader>
          <CardTitle className="text-sm">Conditions Snapshot</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <ConditionChip
            label="Weather"
            value={weatherCondition}
            tone={getWeatherTone(weatherCondition)}
            icon={<CloudSun className="h-4 w-4" />}
          />
          <ConditionChip
            label="Road Condition"
            value={roadCondition}
            tone={getRoadTone(roadCondition)}
            icon={<Route className="h-4 w-4" />}
          />
          <ConditionChip
            label="Visibility"
            value={visibilityCondition}
            tone={getVisibilityTone(visibilityCondition)}
            icon={<Eye className="h-4 w-4" />}
          />
        </CardContent>
      </Card>

      {/* ── Score + breakdown ── */}
      {score != null && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="rounded-xl">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Brain className="h-4 w-4 text-purple-400" /> Safety Score
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center gap-3">
              <ScoreGauge score={score} label={scoreLabel} gpa={scoreGpa} />
              <p className="text-xs text-center text-muted-foreground px-2">
                {score >= 80
                  ? "Good — driver performance within acceptable bounds."
                  : score >= 65
                  ? "Fair — coaching recommended to address identified patterns."
                  : "Poor — immediate intervention advised."}
              </p>
              <div className="mt-1 w-full rounded-lg border border-border bg-muted/50 px-4 py-3 flex items-center justify-between">
                <span className="text-xs text-muted-foreground uppercase tracking-widest">Driver Rating</span>
                {driverScore != null
                  ? <StarRating value={driverScore} />
                  : <span className="text-sm text-muted-foreground">—</span>
                }
              </div>
            </CardContent>
          </Card>

          {hasBreakdown && (
            <Card className="rounded-xl">
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

      {/* ── Full-width smooth driving telemetry graph ── */}
      <Card className="rounded-xl w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            <Brain className="h-4 w-4 text-cyan-400" /> Smooth Driving Telemetry (10-minute pings)
          </CardTitle>
        </CardHeader>
        <CardContent>
          {detail.scoring.smoothness_points.length > 0 ? (
            <SmoothDrivingTelemetryChart points={detail.scoring.smoothness_points} />
          ) : (
            <p className="text-sm text-muted-foreground">
              No smooth driving telemetry is available for this trip yet.
            </p>
          )}
        </CardContent>
      </Card>

      {/* ── XAI narrative ── */}
      {detail.scoring.narrative && (
        <Card className="rounded-xl border border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Brain className="h-4 w-4 text-purple-400" /> Explainability Narrative
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed text-muted-foreground rounded-lg bg-muted/50 px-4 py-3">
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
        <Card className="rounded-xl">
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
            <TripEventMap events={detail.safety_events} />
            <div className="space-y-3 mt-2">
              {detail.safety_events.map((e, i) => (
                <div
                  key={e.event_id}
                  className="rounded-xl border border-border bg-muted/50 p-4 space-y-2"
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
                        {e.location_name ? `${e.location_name} · ` : ""}
                        {e.lat.toFixed(4)}, {e.lon?.toFixed(4)}
                      </span>
                    )}
                    {e.traffic && <span>Traffic: {e.traffic}</span>}
                    {e.weather && <span>Weather: {e.weather}</span>}
                    {e.action && <span>Action: {e.action}</span>}
                  </div>
                  {e.reason && (
                    <p className="text-xs rounded bg-muted/50 px-3 py-2 text-muted-foreground">
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
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <Smile className="h-4 w-4 text-yellow-400" /> Driver Feedback &amp; Sentiment
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-5">

            {/* Feedback quote */}
            {detail.sentiment.feedback_text && (
              <div className="rounded-lg border border-border bg-muted/40 px-4 py-3">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-1.5">
                  Driver&apos;s own words
                </p>
                <p className="text-sm italic leading-relaxed text-foreground">
                  &ldquo;{detail.sentiment.feedback_text}&rdquo;
                </p>
              </div>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Score + label */}
              <div className="flex flex-col items-center justify-center gap-2">
                <div
                  className="text-4xl font-bold"
                  style={{
                    color:
                      detail.sentiment.label === "positive" ? "#22c55e"
                      : detail.sentiment.label === "negative" ? "#ef4444"
                      : "#eab308",
                  }}
                >
                  {detail.sentiment.score != null
                    ? `${Math.round(detail.sentiment.score * 100)}%`
                    : "—"}
                </div>
                <Badge
                  className={`capitalize ${
                    detail.sentiment.label === "positive" ? "bg-green-600"
                    : detail.sentiment.label === "negative" ? "bg-red-600"
                    : "bg-yellow-600"
                  } text-white`}
                >
                  {detail.sentiment.label ?? "Unknown"}
                </Badge>
              </div>

              {/* Emotion bars */}
              <div>
                <p className="text-xs font-semibold uppercase tracking-widest text-muted-foreground mb-3">
                  Emotion Signals
                </p>
                <EmotionBars emotions={detail.sentiment.emotions} />
              </div>
            </div>

            {/* LLM explanation */}
            {detail.sentiment.explanation && (
              <div className="rounded-lg border border-border bg-muted/30 px-4 py-3">
                <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground mb-1.5">
                  Sentiment Agent Analysis
                </p>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  {detail.sentiment.explanation}
                </p>
              </div>
            )}

          </CardContent>
        </Card>
      )}

      {/* ── Coaching ── */}
      {detail.coaching.length > 0 && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm">
              <MessageSquare className="h-4 w-4 text-green-400" /> Coaching Messages
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {detail.coaching.map((c, i) => (
              <div
                key={i}
                className="rounded-xl border border-border bg-muted/50 p-4 space-y-2"
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
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 mt-2">
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
