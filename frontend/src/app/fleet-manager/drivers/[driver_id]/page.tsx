"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getDriverProfile, type DriverProfile } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, User, Car, ShieldAlert, BookOpen } from "lucide-react";

// ── Helpers ───────────────────────────────────────────────────────────────────

function LabelValue({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>
      <span className="text-sm font-medium">{value ?? "—"}</span>
    </div>
  );
}

const STATUS_COLOR: Record<string, string> = {
  active:    "bg-green-600",
  inactive:  "bg-slate-500",
  suspended: "bg-red-600",
};

const EXP_COLOR: Record<string, string> = {
  novice:       "bg-blue-500",
  intermediate: "bg-amber-500",
  expert:       "bg-purple-600",
};

const SEV_COLOR: Record<string, string> = {
  critical: "bg-red-600",
  high:     "bg-orange-500",
  medium:   "bg-yellow-500",
  low:      "bg-blue-500",
};

const DEC_COLOR: Record<string, string> = {
  escalate: "bg-red-600",
  monitor:  "bg-yellow-600",
};

function ScoreChip({ score }: { score: number | null }) {
  if (score === null) return <span className="text-muted-foreground text-xs">—</span>;
  const color = score >= 80 ? "text-green-600" : score >= 60 ? "text-amber-600" : "text-red-600";
  return <span className={`font-mono font-semibold text-sm ${color}`}>{score}</span>;
}

// ── Score trend sparkline ─────────────────────────────────────────────────────

function ScoreTrend({ scores }: { scores: number[] }) {
  if (scores.length === 0) {
    return <p className="text-sm text-muted-foreground">No scored trips yet.</p>;
  }
  const min = Math.min(...scores);
  const max = Math.max(...scores);
  const range = max - min || 1;

  return (
    <div className="flex items-end gap-1.5 h-14">
      {scores.map((s, i) => {
        const heightPct = ((s - min) / range) * 70 + 30; // 30–100%
        const color = s >= 80 ? "bg-green-500" : s >= 60 ? "bg-amber-400" : "bg-red-500";
        return (
          <div key={i} className="flex flex-col items-center gap-0.5 flex-1 min-w-0">
            <span className="text-[9px] text-muted-foreground">{s}</span>
            <div
              className={`w-full rounded-sm ${color} opacity-80`}
              style={{ height: `${heightPct}%` }}
            />
          </div>
        );
      })}
    </div>
  );
}

// ── Fuel battery ──────────────────────────────────────────────────────────────

function FuelBar({ level }: { level: number }) {
  const color = level > 50 ? "bg-green-500" : level > 20 ? "bg-amber-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-3.5 w-24 items-center rounded-sm border border-border p-0.5">
        <div className={`h-full rounded-xs ${color} transition-all`} style={{ width: `${level}%` }} />
      </div>
      <span className="text-xs text-muted-foreground">{level}%</span>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DriverProfilePage() {
  const { driver_id } = useParams<{ driver_id: string }>();
  const router = useRouter();
  const [profile, setProfile] = useState<DriverProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    getDriverProfile(driver_id)
      .then(setProfile)
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [driver_id]);

  if (loading) {
    return (
      <div className="p-8 space-y-4 max-w-5xl mx-auto">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-24 w-full" />
        <div className="grid grid-cols-2 gap-4">
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </div>
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (notFound || !profile || !profile.stats) {
    return (
      <div className="p-8 flex flex-col items-center gap-4 text-center">
        <p className="text-muted-foreground">Driver not found.</p>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
      </div>
    );
  }

  const { stats } = profile;

  const statCards = [
    { label: "Total Trips",     value: stats.total_trips },
    { label: "Avg Score",       value: stats.avg_score ?? "—" },
    { label: "Safety Events",   value: stats.total_events },
    { label: "Critical Events", value: stats.critical_events },
  ];

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex items-start gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back
        </Button>

        <div className="flex items-center gap-4 flex-1">
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-muted">
            <User className="h-7 w-7 text-muted-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">{profile.first_name} {profile.last_name}</h1>
            <p className="text-sm text-muted-foreground">{profile.license_number}</p>
          </div>
          <div className="ml-auto flex gap-2">
            <Badge className={`${STATUS_COLOR[profile.status] ?? "bg-gray-500"} text-white capitalize`}>
              {profile.status}
            </Badge>
            <Badge className={`${EXP_COLOR[profile.experience_level] ?? "bg-gray-500"} text-white capitalize`}>
              {profile.experience_level}
            </Badge>
          </div>
        </div>
      </div>

      {/* ── Stat chips ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {statCards.map(({ label, value }) => (
          <Card key={label} className="rounded-xl text-center py-4">
            <p className="text-2xl font-bold">{value}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{label}</p>
          </Card>
        ))}
      </div>

      {/* ── Identity + Vehicle ─────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-4 w-4" /> Driver Info
            </CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <LabelValue label="Email"      value={profile.email} />
            <LabelValue label="Phone"      value={profile.phone} />
            <LabelValue label="License"    value={profile.license_number} />
            <LabelValue label="Joined"
              value={profile.created_at ? new Date(profile.created_at).toLocaleDateString() : null} />
            <LabelValue label="Experience" value={
              <span className="capitalize">{profile.experience_level}</span>
            } />
            <LabelValue label="Status" value={
              <Badge className={`${STATUS_COLOR[profile.status] ?? "bg-gray-500"} text-white capitalize text-xs`}>
                {profile.status}
              </Badge>
            } />
          </CardContent>
        </Card>

        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Car className="h-4 w-4" /> Assigned Vehicle
            </CardTitle>
          </CardHeader>
          <CardContent>
            {profile.vehicle ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <LabelValue label="Plate"  value={
                    <span className="font-mono font-semibold">{profile.vehicle.license_plate}</span>
                  } />
                  <LabelValue label="Model"  value={`${profile.vehicle.make} ${profile.vehicle.model}`} />
                </div>
                <div className="flex flex-col gap-1.5">
                  <span className="text-xs text-muted-foreground uppercase tracking-wide">Fuel Level</span>
                  <FuelBar level={profile.vehicle.fuel_level} />
                </div>
                {profile.vehicle.has_open_maintenance && (
                  <div className="flex items-center gap-2 rounded-lg bg-amber-50 border border-amber-200 px-3 py-2 text-sm text-amber-700 dark:bg-amber-950/30 dark:border-amber-800 dark:text-amber-400">
                    ⚠ Open maintenance record
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No vehicle assigned.</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ── Score trend ────────────────────────────────────────────────────── */}
      {profile.score_trend.length > 0 && (
        <Card className="rounded-xl">
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-2">
              <CardTitle>Score Trend (last {profile.score_trend.length} trips)</CardTitle>
              <div className="flex gap-4 text-xs text-muted-foreground">
                {stats.min_score !== null && <span>Low: <strong>{stats.min_score}</strong></span>}
                {stats.avg_score !== null && <span>Avg: <strong>{stats.avg_score}</strong></span>}
                {stats.max_score !== null && <span>High: <strong>{stats.max_score}</strong></span>}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScoreTrend scores={profile.score_trend} />
          </CardContent>
        </Card>
      )}

      {/* ── Recent trips ───────────────────────────────────────────────────── */}
      <Card className="rounded-xl">
        <CardHeader>
          <CardTitle>Recent Trips</CardTitle>
        </CardHeader>
        <CardContent>
          {profile.recent_trips.length === 0 ? (
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
                {profile.recent_trips.map((t) => (
                  <tr
                    key={t.trip_id}
                    onClick={() => router.push(`/fleet-manager/trips/${t.trip_id}`)}
                    className="cursor-pointer border-t border-border/50 hover:bg-muted/30 transition-colors"
                  >
                    <td className="px-4 py-2.5 font-mono text-xs text-muted-foreground">{t.trip_id.slice(0, 8)}</td>
                    <td className="px-4 py-2.5">{t.route_name ?? "—"}</td>
                    <td className="px-4 py-2.5 capitalize">{t.status}</td>
                    <td className="px-4 py-2.5"><ScoreChip score={t.score} /></td>
                    <td className="px-4 py-2.5 text-xs text-muted-foreground">
                      {t.created_at ? new Date(t.created_at).toLocaleDateString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>

      {/* ── Safety events ──────────────────────────────────────────────────── */}
      {profile.safety_events.length > 0 && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4" /> Safety Events
            </CardTitle>
          </CardHeader>
          <CardContent>
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
                {profile.safety_events.map((e) => (
                  <tr
                    key={e.event_id}
                    onClick={() => router.push(`/fleet-manager/issues/${e.event_id}`)}
                    className="cursor-pointer border-t border-border/50 hover:bg-muted/30 transition-colors"
                  >
                    <td className="px-4 py-2.5 capitalize">{e.event_type.replace(/_/g, " ")}</td>
                    <td className="px-4 py-2.5">
                      <Badge className={`${SEV_COLOR[e.severity?.toLowerCase()] ?? "bg-gray-500"} text-white capitalize text-xs`}>
                        {e.severity}
                      </Badge>
                    </td>
                    <td className="px-4 py-2.5">
                      {e.decision
                        ? <Badge className={`${DEC_COLOR[e.decision.toLowerCase()] ?? "bg-gray-500"} text-white capitalize text-xs`}>{e.decision}</Badge>
                        : <span className="text-muted-foreground">—</span>}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-muted-foreground">
                      {e.event_timestamp ? new Date(e.event_timestamp).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}

      {/* ── Coaching history ───────────────────────────────────────────────── */}
      {profile.coaching.length > 0 && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" /> Coaching History
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {profile.coaching.map((c, i) => (
              <div key={i} className="rounded-lg border border-border bg-muted/30 px-4 py-3 space-y-1">
                <div className="flex items-center gap-2">
                  <span className={`rounded px-1.5 py-0.5 text-[10px] font-bold text-white capitalize ${
                    c.priority === "high" ? "bg-red-600" : c.priority === "medium" ? "bg-amber-500" : "bg-blue-500"
                  }`}>{c.priority}</span>
                  <span className="text-xs font-medium capitalize">{c.category.replace(/_/g, " ")}</span>
                  <span className="ml-auto text-[10px] text-muted-foreground">
                    {c.created_at ? new Date(c.created_at).toLocaleDateString() : ""}
                  </span>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">{c.message}</p>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

    </div>
  );
}
