"use client";

import { useEffect, useRef, useState } from "react";
import { getRoutes, getRouteHeatmap, type Route, type RouteHeatPoint } from "@/lib/api";
import { Badge } from "@/components/ui/badge";
import { MapPin, Navigation, AlertTriangle, Truck } from "lucide-react";

const SEVERITY_WEIGHT: Record<string, number> = {
  critical: 3,
  high: 2,
  medium: 1,
  low: 0.5,
};

const ROUTE_TYPE_COLOR: Record<string, string> = {
  highway: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  urban: "bg-orange-500/20 text-orange-400 border-orange-500/30",
  mixed: "bg-purple-500/20 text-purple-400 border-purple-500/30",
};

export default function RoutesPage() {
  const [routes, setRoutes] = useState<Route[]>([]);
  const [selected, setSelected] = useState<Route | null>(null);
  const [heatPoints, setHeatPoints] = useState<RouteHeatPoint[]>([]);
  const [loadingHeat, setLoadingHeat] = useState(false);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<any>(null);
  const mapReadyRef = useRef(false);

  // Load routes
  useEffect(() => {
    getRoutes().then(setRoutes).catch(console.error);
  }, []);

  // Init map once
  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token || !mapContainerRef.current) return;
    let map: any;

    async function init() {
      const mapboxgl = (await import("mapbox-gl")).default;
      await import("mapbox-gl/dist/mapbox-gl.css");
      if (!mapContainerRef.current) return;
      mapboxgl.accessToken = token!;
      map = new mapboxgl.Map({
        container: mapContainerRef.current,
        style: "mapbox://styles/mapbox/dark-v11",
        center: [103.82, 1.35],
        zoom: 11,
        minZoom: 9,
      });
      map.addControl(new mapboxgl.NavigationControl(), "top-right");
      map.on("load", () => {
        mapReadyRef.current = true;
        mapRef.current = map;

        // Add sources/layers upfront (empty)
        map.addSource("route-line", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
        map.addLayer({
          id: "route-line-bg", type: "line", source: "route-line",
          paint: { "line-color": "#6366f1", "line-width": 6, "line-opacity": 0.3, "line-blur": 4 },
        });
        map.addLayer({
          id: "route-line-fg", type: "line", source: "route-line",
          paint: {
            "line-color": "#818cf8",
            "line-width": 3,
            "line-dasharray": [0, 2],
          },
        });

        map.addSource("events", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
        map.addLayer({
          id: "events-heat", type: "heatmap", source: "events",
          paint: {
            "heatmap-weight": ["get", "weight"],
            "heatmap-intensity": ["interpolate", ["linear"], ["zoom"], 9, 0.6, 15, 2],
            "heatmap-radius": ["interpolate", ["linear"], ["zoom"], 9, 20, 15, 50],
            "heatmap-opacity": 0.85,
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
          },
        });

        map.addSource("endpoints", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
        map.addLayer({
          id: "endpoints-circle", type: "circle", source: "endpoints",
          paint: {
            "circle-radius": 10,
            "circle-color": ["match", ["get", "kind"], "start", "#22c55e", "#ef4444"],
            "circle-stroke-color": "#fff",
            "circle-stroke-width": 2,
          },
        });
      });
    }
    init();
    return () => { map?.remove(); mapRef.current = null; mapReadyRef.current = false; };
  }, []);

  // When a route is selected: fetch heatmap + draw route line
  useEffect(() => {
    if (!selected) return;
    const map = mapRef.current;

    // Fetch heatmap data
    setLoadingHeat(true);
    getRouteHeatmap(selected.id)
      .then(setHeatPoints)
      .catch(() => setHeatPoints([]))
      .finally(() => setLoadingHeat(false));

    // Draw route line via Mapbox Directions API if coords exist
    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    const { start_lat, start_lon, end_lat, end_lon } = selected;
    if (map && mapReadyRef.current && start_lat && start_lon && end_lat && end_lon && token) {
      const url = `https://api.mapbox.com/directions/v5/mapbox/driving/${start_lon},${start_lat};${end_lon},${end_lat}?geometries=geojson&access_token=${token}`;
      fetch(url)
        .then((r) => r.json())
        .then((data) => {
          const geometry = data.routes?.[0]?.geometry;
          if (!geometry) return;
          (map.getSource("route-line") as any)?.setData({
            type: "FeatureCollection",
            features: [{ type: "Feature", geometry, properties: {} }],
          });
        })
        .catch(() => {
          // Fallback: straight line
          (map.getSource("route-line") as any)?.setData({
            type: "FeatureCollection",
            features: [{
              type: "Feature",
              geometry: { type: "LineString", coordinates: [[start_lon, start_lat], [end_lon, end_lat]] },
              properties: {},
            }],
          });
        });

      // Endpoint markers
      (map.getSource("endpoints") as any)?.setData({
        type: "FeatureCollection",
        features: [
          { type: "Feature", geometry: { type: "Point", coordinates: [start_lon, start_lat] }, properties: { kind: "start" } },
          { type: "Feature", geometry: { type: "Point", coordinates: [end_lon, end_lat] }, properties: { kind: "end" } },
        ],
      });

      // Fit bounds
      const bounds: [[number, number], [number, number]] = [
        [Math.min(start_lon, end_lon) - 0.02, Math.min(start_lat, end_lat) - 0.02],
        [Math.max(start_lon, end_lon) + 0.02, Math.max(start_lat, end_lat) + 0.02],
      ];
      map.fitBounds(bounds, { padding: 80, duration: 1000 });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected]);

  // Push heatmap data to map whenever heatPoints change
  useEffect(() => {
    const map = mapRef.current;
    if (!map || !mapReadyRef.current) return;
    const geojson = {
      type: "FeatureCollection" as const,
      features: heatPoints.map((e) => ({
        type: "Feature" as const,
        geometry: { type: "Point" as const, coordinates: [e.lon, e.lat] },
        properties: {
          weight: SEVERITY_WEIGHT[e.severity?.toLowerCase()] ?? 1,
          severity: e.severity ?? "low",
          event_type: e.event_type ?? "",
        },
      })),
    };
    (map.getSource("events") as any)?.setData(geojson);
  }, [heatPoints]);

  const criticalCount = heatPoints.filter((e) => e.severity === "critical").length;
  const highCount = heatPoints.filter((e) => e.severity === "high").length;

  return (
    <div className="-m-2 md:-m-3 flex h-[calc(100vh-3.5rem)] overflow-hidden">
      {/* ── Left sidebar ─────────────────────────────────────────────────── */}
      <div className="w-80 flex-shrink-0 flex flex-col bg-card border-r border-border overflow-hidden">
        {/* Sidebar header */}
        <div className="px-4 py-3 border-b border-border">
          <h2 className="text-sm font-bold uppercase tracking-tight">Routes</h2>
          <p className="text-xs text-muted-foreground mt-0.5">{routes.length} corridors</p>
        </div>

        {/* Route list */}
        <div className="flex-1 overflow-y-auto">
          {routes.map((route) => {
            const isSelected = selected?.id === route.id;
            return (
              <button
                key={route.id}
                onClick={() => setSelected(route)}
                className={`w-full text-left px-4 py-3 border-b border-border/50 transition-colors hover:bg-muted/50 ${
                  isSelected ? "bg-muted border-l-2 border-l-indigo-500" : ""
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-semibold truncate">{route.name}</p>
                    <div className="flex items-center gap-1 mt-1">
                      <MapPin className="h-3 w-3 text-green-500 flex-shrink-0" />
                      <span className="text-[10px] text-muted-foreground truncate">{route.start_location}</span>
                    </div>
                    <div className="flex items-center gap-1 mt-0.5">
                      <Navigation className="h-3 w-3 text-red-500 flex-shrink-0" />
                      <span className="text-[10px] text-muted-foreground truncate">{route.end_location}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1 flex-shrink-0">
                    <Badge variant="outline" className={`text-[9px] px-1.5 py-0 ${ROUTE_TYPE_COLOR[route.route_type] ?? ""}`}>
                      {route.route_type}
                    </Badge>
                    {route.distance_km && (
                      <span className="text-[10px] text-muted-foreground">{Number(route.distance_km).toFixed(0)} km</span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Selected route info panel */}
        {selected && (
          <div className="border-t border-border p-4 bg-muted/30">
            <p className="text-xs font-semibold mb-2">{selected.name}</p>
            {loadingHeat ? (
              <p className="text-xs text-muted-foreground">Loading events…</p>
            ) : (
              <div className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Total events</span>
                  <span className="font-semibold">{heatPoints.length}</span>
                </div>
                {criticalCount > 0 && (
                  <div className="flex items-center gap-1.5 text-xs text-red-400">
                    <AlertTriangle className="h-3 w-3" />
                    <span>{criticalCount} critical</span>
                  </div>
                )}
                {highCount > 0 && (
                  <div className="flex items-center gap-1.5 text-xs text-orange-400">
                    <AlertTriangle className="h-3 w-3" />
                    <span>{highCount} high severity</span>
                  </div>
                )}
                {heatPoints.length === 0 && (
                  <p className="text-xs text-muted-foreground">No events recorded yet.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Map ──────────────────────────────────────────────────────────── */}
      <div className="flex-1 relative">
        <div ref={mapContainerRef} className="h-full w-full" />

        {/* Empty state overlay */}
        {!selected && (
          <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
            <div className="bg-black/60 backdrop-blur-sm rounded-xl px-6 py-4 text-center">
              <Truck className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm font-medium text-white">Select a route</p>
              <p className="text-xs text-white/50 mt-1">to view the path and incident heatmap</p>
            </div>
          </div>
        )}

        {/* Heatmap legend */}
        {selected && heatPoints.length > 0 && (
          <div className="absolute bottom-6 right-4 rounded-lg bg-black/70 px-3 py-2 backdrop-blur-sm">
            <p className="mb-1.5 text-[10px] font-bold uppercase tracking-widest text-white/60">Incident Density</p>
            <div className="flex items-center gap-2">
              <div className="h-2 w-24 rounded-full"
                style={{ background: "linear-gradient(to right, #fef08a, #fbbf24, #f97316, #dc2626, #7f1d1d)" }} />
              <div className="flex w-20 justify-between text-[9px] text-white/50">
                <span>Low</span><span>High</span>
              </div>
            </div>
          </div>
        )}

        {/* Endpoint legend */}
        {selected && (
          <div className="absolute top-4 left-4 rounded-lg bg-black/70 px-3 py-2 backdrop-blur-sm space-y-1">
            <div className="flex items-center gap-2 text-xs text-white/80">
              <span className="inline-block h-3 w-3 rounded-full bg-green-500 ring-1 ring-white/30" />
              {selected.start_location}
            </div>
            <div className="flex items-center gap-2 text-xs text-white/80">
              <span className="inline-block h-3 w-3 rounded-full bg-red-500 ring-1 ring-white/30" />
              {selected.end_location}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
