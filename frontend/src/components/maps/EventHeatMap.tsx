"use client";

import { useEffect, useRef, useState } from "react";
import { MapBase } from "./MapBase";
import { MapLayerControl } from "./MapLayerControl";
import { WeatherWidget } from "./WeatherWidget";

export type HeatPoint = {
  lat: number;
  lon: number;
  severity: string;
  event_type?: string;
};

type Props = {
  events: HeatPoint[];
  height?: number;
};

const SEVERITY_WEIGHT: Record<string, number> = {
  critical: 3,
  high:     2,
  medium:   1,
  low:      0.5,
};

export function EventHeatMap({ events, height = 420 }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapRef       = useRef<any>(null);
  const rainAddedRef = useRef(false);
  const tempAddedRef = useRef(false);
  const owmToken     = process.env.NEXT_PUBLIC_OWM_TOKEN ?? "";

  const [showTraffic, setShowTraffic] = useState(false);
  const [showRain, setShowRain]       = useState(false);
  const [showTemp, setShowTemp]       = useState(false);

  const points = events.filter((e) => e.lat != null && e.lon != null);

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
          tileSize: 256,
          attribution: "© OpenWeatherMap",
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

  function handleLoad(map: any) {
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

    // Event heatmap
    const geojson = {
      type: "FeatureCollection" as const,
      features: points.map((e) => ({
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [e.lon, e.lat] },
        properties: {
          weight:     SEVERITY_WEIGHT[e.severity?.toLowerCase()] ?? 1,
          severity:   e.severity ?? "low",
          event_type: e.event_type ?? "",
        },
      })),
    };

    map.addSource("events", { type: "geojson", data: geojson });
    map.addLayer({
      id: "events-heat", type: "heatmap", source: "events",
      paint: {
        "heatmap-weight":    ["get", "weight"],
        "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 9, 0.6, 15, 2],
        "heatmap-radius":    ["interpolate", ["linear"], ["zoom"], 9, 20, 15, 50],
        "heatmap-opacity":   0.8,
        "heatmap-color": [
          "interpolate", ["linear"], ["heatmap-density"],
          0, "rgba(0,0,0,0)", 0.15, "#fef08a",
          0.35, "#fbbf24", 0.6, "#f97316",
          0.8, "#dc2626", 1, "#7f1d1d",
        ],
      },
    });
    map.addLayer({
      id: "events-dots", type: "circle", source: "events", minzoom: 13,
      paint: {
        "circle-radius": 6,
        "circle-color": ["match", ["get", "severity"],
          "critical", "#dc2626", "high", "#f97316", "medium", "#fbbf24", "#22c55e"],
        "circle-stroke-color": "#fff",
        "circle-stroke-width": 1.5,
        "circle-opacity": 0.9,
      },
    });
  }

  return (
    <MapBase
      height={height}
      empty={points.length === 0}
      emptyMessage="No events with location data to display."
      deps={[points.length]}
      onLoad={handleLoad}
    >
      {/* Persistent weather strip */}
      <WeatherWidget />

      {/* Density legend */}
      <div className="absolute bottom-8 right-3 z-10 rounded-lg bg-black/60 px-3 py-2 backdrop-blur-sm">
        <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-white/60">
          Event Density
        </p>
        <div className="flex items-center gap-2">
          <div className="h-2 w-24 rounded-full"
            style={{ background: "linear-gradient(to right, #fef08a, #fbbf24, #f97316, #dc2626, #7f1d1d)" }} />
          <div className="flex w-24 justify-between text-[9px] text-white/50">
            <span>Low</span><span>High</span>
          </div>
        </div>
      </div>

      {/* Layer toggles */}
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
