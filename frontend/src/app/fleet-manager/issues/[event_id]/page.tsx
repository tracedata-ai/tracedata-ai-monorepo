"use client";

import { useEffect, useRef, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getSafetyEvent, type SafetyEvent } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeft, ExternalLink, MapPin } from "lucide-react";

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

function EventMap({ lat, lon }: { lat: number; lon: number }) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token) {
      setError("NEXT_PUBLIC_MAPBOX_TOKEN is not set.");
      return;
    }

    let map: { remove: () => void } | null = null;

    async function initMap() {
      try {
        const mapboxgl = (await import("mapbox-gl")).default;
        mapboxgl.accessToken = token;

        if (!mapContainerRef.current) return;

        map = new mapboxgl.Map({
          container: mapContainerRef.current,
          style: "mapbox://styles/mapbox/light-v11",
          center: [lon, lat],
          zoom: 13,
        });

        new mapboxgl.Marker({ color: "#ef4444" })
          .setLngLat([lon, lat])
          .setPopup(
            new mapboxgl.Popup({ offset: 25 }).setHTML(
              `<div style="color:#000;font-size:12px;">
                <strong>Event Location</strong><br/>
                Lat: ${lat.toFixed(5)}<br/>
                Lon: ${lon.toFixed(5)}
              </div>`
            )
          )
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          .addTo(map as any);
      } catch (e) {
        setError(String(e));
      }
    }

    initMap();

    return () => {
      map?.remove();
    };
  }, [lat, lon]);

  if (error) {
    return (
      <div className="flex h-64 items-center justify-center rounded-xl bg-muted/50 text-sm text-muted-foreground">
        <MapPin className="mr-2 h-4 w-4" />
        Map unavailable: {error}
      </div>
    );
  }

  return (
    <div
      ref={mapContainerRef}
      className="h-72 w-full rounded-xl overflow-hidden border border-white/10"
    />
  );
}

export default function SafetyEventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const eventId = params.event_id as string;

  const [event, setEvent] = useState<SafetyEvent | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    getSafetyEvent(eventId)
      .then(setEvent)
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
            <EventMap lat={event.lat} lon={event.lon} />
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
            <LabelValue label="Driver" value={event.driver_id} />
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

      {/* Video evidence */}
      {event.video_url && (
        <Card className="rounded-xl">
          <CardHeader>
            <CardTitle>Video Evidence</CardTitle>
          </CardHeader>
          <CardContent>
            <a
              href={event.video_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 underline"
            >
              <ExternalLink className="h-4 w-4" />
              View Recording
            </a>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
