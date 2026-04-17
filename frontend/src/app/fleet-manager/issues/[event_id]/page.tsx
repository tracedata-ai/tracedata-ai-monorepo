"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getSafetyEvent, getSafetyEvents, type SafetyEvent } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, MapPin, Camera, X } from "lucide-react";
import { MapBase } from "@/components/maps/MapBase";
import { MapLayerControl } from "@/components/maps/MapLayerControl";
import { WeatherWidget } from "@/components/maps/WeatherWidget";
import Image from "next/image";

const severityClass: Record<string, string> = {
  critical: "bg-red-600",
  high: "bg-orange-500",
  medium: "bg-yellow-500",
  low: "bg-blue-500",
};

const decisionClass: Record<string, string> = {
  escalate: "bg-red-600",
  monitor: "bg-yellow-600",
};

function LabelValue({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-xs text-muted-foreground uppercase tracking-wide">{label}</span>
      <span className="text-sm font-medium">{value ?? "—"}</span>
    </div>
  );
}

// ── Dashcam Evidence ──────────────────────────────────────────────────────────

const MOCK_IMAGES = ["/dashcam/image1.png", "/dashcam/image2.png", "/dashcam/image3.png"];
const MOCK_VIDEO  = "/dashcam/video.mp4";

function DashcamEvidence({ eventId }: { eventId: string }) {
  const [lightbox, setLightbox] = useState<string | null>(null);

  return (
    <>
      <Card className="rounded-xl overflow-hidden">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between gap-3 flex-wrap">
            <CardTitle className="flex items-center gap-2">
              <Camera className="h-4 w-4" /> Dashcam Evidence
            </CardTitle>
            <span className="font-mono text-[10px] text-muted-foreground bg-muted rounded px-2 py-1 truncate max-w-xs">
              s3://tracedata-dashcam/incidents/{eventId.slice(0, 8)}/
            </span>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">

          {/* Image strip */}
          <div className="grid grid-cols-3 gap-2">
            {MOCK_IMAGES.map((src, i) => (
              <button
                key={i}
                onClick={() => setLightbox(src)}
                className="group relative aspect-video overflow-hidden rounded-lg border border-border focus:outline-none focus:ring-2 focus:ring-primary/40"
              >
                <Image
                  src={src}
                  alt={`Dashcam frame ${i + 1}`}
                  fill
                  className="object-cover transition-transform duration-300 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-black/0 transition-colors group-hover:bg-black/20" />
                <span className="absolute bottom-1.5 left-1.5 rounded bg-black/50 px-1.5 py-0.5 font-mono text-[9px] text-white/80">
                  CAM {i + 1}
                </span>
              </button>
            ))}
          </div>

          {/* Video player */}
          <div className="overflow-hidden rounded-lg border border-border bg-black">
            {/* eslint-disable-next-line jsx-a11y/media-has-caption */}
            <video
              controls
              className="w-full max-h-72"
              poster={MOCK_IMAGES[0]}
              preload="metadata"
            >
              <source src={MOCK_VIDEO} type="video/mp4" />
            </video>
          </div>

        </CardContent>
      </Card>

      {/* Lightbox */}
      {lightbox && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-sm"
          onClick={() => setLightbox(null)}
        >
          <button
            className="absolute top-4 right-4 flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20"
            onClick={() => setLightbox(null)}
          >
            <X className="h-4 w-4" />
          </button>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={lightbox}
            alt="Dashcam frame"
            className="max-h-[90vh] max-w-[90vw] rounded-xl object-contain shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </>
  );
}

// ── Heatmap + event marker ─────────────────────────────────────────────────────

const SEVERITY_WEIGHT: Record<string, number> = {
  critical: 3, high: 2, medium: 1, low: 0.5,
};

function EventMap({
  lat, lon, allEvents,
}: {
  lat: number;
  lon: number;
  allEvents: SafetyEvent[];
}) {
  const points = allEvents.filter((e) => e.lat != null && e.lon != null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapRef       = useRef<any>(null);
  const rainAddedRef = useRef(false);
  const tempAddedRef = useRef(false);
  const owmToken     = process.env.NEXT_PUBLIC_OWM_TOKEN ?? "";

  const [showTraffic, setShowTraffic] = useState(false);
  const [showRain, setShowRain]       = useState(false);
  const [showTemp, setShowTemp]       = useState(false);

  useEffect(() => {
    const map = mapRef.current;
    if (!map?.getLayer("traffic-flow")) return;
    map.setLayoutProperty("traffic-flow", "visibility", showTraffic ? "visible" : "none");
  }, [showTraffic]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !owmToken) return;
    if (showRain) {
      if (!rainAddedRef.current) {
        map.addSource("owm-rain", {
          type: "raster",
          tiles: [`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${owmToken}`],
          tileSize: 256, attribution: "© OpenWeatherMap",
        });
        map.addLayer({ id: "owm-rain-layer", type: "raster", source: "owm-rain",
          paint: { "raster-opacity": 0.65 } }, "traffic-flow");
        rainAddedRef.current = true;
      } else {
        map.setLayoutProperty("owm-rain-layer", "visibility", "visible");
      }
    } else if (rainAddedRef.current) {
      map.setLayoutProperty("owm-rain-layer", "visibility", "none");
    }
  }, [showRain, owmToken]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !owmToken) return;
    if (showTemp) {
      if (!tempAddedRef.current) {
        map.addSource("owm-temp", {
          type: "raster",
          tiles: [`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${owmToken}`],
          tileSize: 256, attribution: "© OpenWeatherMap",
        });
        map.addLayer({ id: "owm-temp-layer", type: "raster", source: "owm-temp",
          paint: { "raster-opacity": 0.5 } }, "traffic-flow");
        tempAddedRef.current = true;
      } else {
        map.setLayoutProperty("owm-temp-layer", "visibility", "visible");
      }
    } else if (tempAddedRef.current) {
      map.setLayoutProperty("owm-temp-layer", "visibility", "none");
    }
  }, [showTemp, owmToken]);

  const handleLoad = useCallback((map: any, mapboxgl: any) => {
    mapRef.current = map;
    rainAddedRef.current = false;
    tempAddedRef.current = false;

    // Traffic
    map.addSource("mapbox-traffic", { type: "vector", url: "mapbox://mapbox.mapbox-traffic-v1" });
    map.addLayer({
      id: "traffic-flow", type: "line", source: "mapbox-traffic",
      "source-layer": "traffic",
      layout: { visibility: "none" },
      paint: {
        "line-width": 2.5, "line-opacity": 0.85,
        "line-color": ["match", ["get", "congestion"],
          "low", "#22c55e", "moderate", "#fbbf24",
          "heavy", "#f97316", "severe", "#dc2626", "#94a3b8"],
      },
    });

    // Heatmap of all events
    const geojson = {
      type: "FeatureCollection" as const,
      features: points.map((e) => ({
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [e.lon!, e.lat!] },
        properties: { weight: SEVERITY_WEIGHT[e.severity?.toLowerCase()] ?? 1 },
      })),
    };
    map.addSource("all-events", { type: "geojson", data: geojson });
    map.addLayer({
      id: "all-events-heat", type: "heatmap", source: "all-events",
      paint: {
        "heatmap-weight":    ["get", "weight"],
        "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 9, 0.6, 15, 2],
        "heatmap-radius":    ["interpolate", ["linear"], ["zoom"], 9, 20, 15, 50],
        "heatmap-opacity":   0.7,
        "heatmap-color": ["interpolate", ["linear"], ["heatmap-density"],
          0, "rgba(0,0,0,0)", 0.15, "#fef08a",
          0.35, "#fbbf24", 0.6, "#f97316", 0.8, "#dc2626", 1, "#7f1d1d"],
      },
    });

    // Pulsing marker for this event
    const el   = document.createElement("div");
    el.style.cssText = "position:relative;width:20px;height:20px;";
    const ring = document.createElement("div");
    ring.style.cssText = `position:absolute;inset:0;border-radius:50%;
      border:2px solid #ef4444;animation:pulse-ring 1.8s ease-out infinite;`;
    const dot  = document.createElement("div");
    dot.style.cssText = `position:absolute;inset:4px;border-radius:50%;
      background:#ef4444;border:2px solid white;box-shadow:0 0 8px rgba(239,68,68,0.8);`;
    el.appendChild(ring);
    el.appendChild(dot);
    new mapboxgl.Marker({ element: el })
      .setLngLat([lon, lat])
      .setPopup(new mapboxgl.Popup({ offset: 20 }).setHTML(
        `<div style="font-size:12px;color:#111;padding:2px 4px;">
          <strong>Event Location</strong><br/>${lat.toFixed(5)}, ${lon.toFixed(5)}</div>`
      ))
      .addTo(map);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lon, points.length]);

  return (
    <MapBase height={320} center={[lon, lat]} zoom={13} onLoad={handleLoad} deps={[lat, lon, points.length]}>
      {/* Persistent weather strip */}
      <WeatherWidget lat={lat} lon={lon} />

      {/* Density legend — right side, below weather widget */}
      <div className="absolute bottom-8 right-3 z-10 rounded-lg bg-black/60 px-2.5 py-1.5 backdrop-blur-sm">
        <p className="mb-1 text-[9px] font-bold uppercase tracking-widest text-white/60">Area Density</p>
        <div className="flex items-center gap-1.5">
          <div className="h-1.5 w-20 rounded-full"
            style={{ background: "linear-gradient(to right, #fef08a, #fbbf24, #f97316, #dc2626, #7f1d1d)" }} />
          <div className="flex w-20 justify-between text-[8px] text-white/50">
            <span>Low</span><span>High</span>
          </div>
        </div>
      </div>
      <MapLayerControl
        showTraffic={showTraffic}
        onTrafficToggle={() => setShowTraffic((v) => !v)}
        showRain={showRain}
        onRainToggle={() => setShowRain((v) => !v)}
        showTemp={showTemp}
        onTempToggle={() => setShowTemp((v) => !v)}
        hasOWM={!!owmToken}
      />
    </MapBase>
  );
}

export default function SafetyEventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.event_id as string;

  const [event, setEvent]       = useState<SafetyEvent | null>(null);
  const [allEvents, setAllEvents] = useState<SafetyEvent[]>([]);
  const [loading, setLoading]   = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    Promise.all([getSafetyEvent(eventId), getSafetyEvents()])
      .then(([ev, all]) => { setEvent(ev); setAllEvents(all); })
      .catch(() => setNotFound(true))
      .finally(() => setLoading(false));
  }, [eventId]);

  if (loading) {
    return (
      <div className="p-8 space-y-4">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-72 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (notFound || !event) {
    return (
      <div className="p-8 flex flex-col items-center gap-4 text-center">
        <p className="text-muted-foreground">Event not found.</p>
        <Button variant="outline" onClick={() => router.back()}>
          <ArrowLeft className="mr-2 h-4 w-4" /> Back
        </Button>
      </div>
    );
  }

  const sevClass = severityClass[event.severity?.toLowerCase()] ?? "bg-gray-500";
  const decClass = decisionClass[event.decision?.toLowerCase() ?? ""] ?? "bg-gray-500";

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      {/* Back + title */}
      <div className="flex items-center gap-4">
        <Button variant="outline" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="mr-1 h-4 w-4" /> Back
        </Button>
        <div>
          <h1 className="text-xl font-semibold capitalize">
            {event.event_type.replace(/_/g, " ")}
          </h1>
          <p className="text-xs text-muted-foreground">{event.event_id}</p>
        </div>
        <div className="ml-auto flex gap-2">
          <Badge className={`${sevClass} text-white capitalize`}>{event.severity}</Badge>
          {event.decision && (
            <Badge className={`${decClass} text-white capitalize`}>{event.decision}</Badge>
          )}
          {event.llm_path && (
            <Badge className="bg-purple-600 text-white">LLM Analysed</Badge>
          )}
        </div>
      </div>

      {/* Map */}
      {event.lat != null && event.lon != null ? (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-4 w-4" /> Event Location
            </CardTitle>
          </CardHeader>
          <CardContent>
            <EventMap lat={event.lat} lon={event.lon} allEvents={allEvents} />
            <p className="mt-2 text-xs text-muted-foreground">
              {event.lat.toFixed(5)}, {event.lon.toFixed(5)}
            </p>
          </CardContent>
        </Card>
      ) : null}

      {/* Trip context + event info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle>Trip Context</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <LabelValue label="Trip ID" value={event.trip_id} />
            <LabelValue label="Truck" value={event.truck_id} />
            <LabelValue label="Driver" value={event.driver_name} />
            <LabelValue label="Route" value={event.route_name} />
            <LabelValue
              label="Trip Started"
              value={event.trip_started_at ? new Date(event.trip_started_at).toLocaleString() : null}
            />
            <LabelValue
              label="Event Time"
              value={event.event_timestamp ? new Date(event.event_timestamp).toLocaleString() : null}
            />
          </CardContent>
        </Card>

        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle>Conditions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <LabelValue label="Traffic" value={event.traffic_conditions} />
            <LabelValue label="Weather" value={event.weather_conditions} />
            <LabelValue label="Assessed Severity" value={event.assessed_severity} />
          </CardContent>
        </Card>
      </div>

      {/* Safety decision */}
      {(event.decision || event.action || event.reason || event.recommended_action) && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle>Safety Agent Decision</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <LabelValue label="Decision" value={event.decision} />
              <LabelValue label="Action" value={event.action} />
            </div>
            {event.reason && (
              <div className="flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Reason</span>
                <p className="text-sm leading-relaxed rounded-lg bg-muted/50 px-3 py-2">{event.reason}</p>
              </div>
            )}
            {event.recommended_action && (
              <div className="flex flex-col gap-1">
                <span className="text-xs text-muted-foreground uppercase tracking-wide">Recommended Action</span>
                <p className="text-sm leading-relaxed rounded-lg bg-muted/50 px-3 py-2">{event.recommended_action}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Analysis */}
      {event.analysis_reason && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle>Analysis</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed rounded-lg bg-muted/50 px-3 py-2">{event.analysis_reason}</p>
          </CardContent>
        </Card>
      )}

      {/* Dashcam evidence */}
      <DashcamEvidence eventId={event.event_id} />

      {/* External recording link — superseded by dashcam evidence above
      {event.video_url && (
        <Card className="rounded-xl">
          <CardHeader><CardTitle>External Recording</CardTitle></CardHeader>
          <CardContent>
            <a href={event.video_url} target="_blank" rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 underline">
              <ExternalLink className="h-4 w-4" /> View Recording
            </a>
          </CardContent>
        </Card>
      )} */}
    </div>
  );
}
