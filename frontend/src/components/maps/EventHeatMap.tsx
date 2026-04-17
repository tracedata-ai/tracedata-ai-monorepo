"use client";

import { MapBase } from "./MapBase";

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
  const points = events.filter((e) => e.lat != null && e.lon != null);

  function handleLoad(map: any) {
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

    // Heatmap — yellow (sparse) → orange → red (dense)
    map.addLayer({
      id:     "events-heat",
      type:   "heatmap",
      source: "events",
      paint: {
        "heatmap-weight":     ["get", "weight"],
        "heatmap-intensity":  ["interpolate", ["linear"], ["zoom"], 9, 0.6, 15, 2],
        "heatmap-radius":     ["interpolate", ["linear"], ["zoom"], 9, 20, 15, 50],
        "heatmap-opacity":    0.8,
        "heatmap-color": [
          "interpolate", ["linear"], ["heatmap-density"],
          0,    "rgba(0,0,0,0)",
          0.15, "#fef08a",
          0.35, "#fbbf24",
          0.6,  "#f97316",
          0.8,  "#dc2626",
          1,    "#7f1d1d",
        ],
      },
    });

    // Individual dots at high zoom
    map.addLayer({
      id:       "events-dots",
      type:     "circle",
      source:   "events",
      minzoom:  13,
      paint: {
        "circle-radius": 6,
        "circle-color": [
          "match", ["get", "severity"],
          "critical", "#dc2626",
          "high",     "#f97316",
          "medium",   "#fbbf24",
          "#22c55e",
        ],
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
      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-10 rounded-lg bg-black/60 px-3 py-2 backdrop-blur-sm">
        <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-white/60">
          Event Density
        </p>
        <div className="flex items-center gap-2">
          <div
            className="h-2 w-24 rounded-full"
            style={{ background: "linear-gradient(to right, #fef08a, #fbbf24, #f97316, #dc2626, #7f1d1d)" }}
          />
          <div className="flex w-24 justify-between text-[9px] text-white/50">
            <span>Low</span>
            <span>High</span>
          </div>
        </div>
      </div>
    </MapBase>
  );
}
