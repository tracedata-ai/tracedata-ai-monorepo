"use client";

import { useCallback, useRef, useState } from "react";
import { Search, X } from "lucide-react";
import { MapBase } from "./MapBase";
import { VehicleCardMini } from "@/components/fleet/VehicleCard";

export type VehiclePin = {
  id: string;
  licensePlate: string;
  model: string;
  status: string;
  lat: number;
  lng: number;
  imageIndex: number;
  fuelLevel?: number;
  hasOpenMaintenance?: boolean;
};

type Props = {
  vehicles: VehiclePin[];
  height?: number;
};

const STATUS_COLOR: Record<string, string> = {
  active:         "#22c55e",
  in_maintenance: "#ef4444",
  inactive:       "#64748b",
};

export function FleetMap({ vehicles, height = 400 }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const mapRef    = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const markersRef = useRef<Map<string, any>>(new Map());

  const [query, setQuery]           = useState("");
  const [dropdownOpen, setDropdown] = useState(false);
  const [selected, setSelected]     = useState<VehiclePin | null>(null);
  const [hovered, setHovered]       = useState<{ vehicle: VehiclePin; x: number; y: number } | null>(null);

  const suggestions = query.trim()
    ? vehicles.filter(
        (v) =>
          v.licensePlate.toLowerCase().includes(query.toLowerCase()) ||
          v.model.toLowerCase().includes(query.toLowerCase())
      )
    : [];

  const handleLoad = useCallback((map: any, mapboxgl: any) => {
    mapRef.current = map;
    markersRef.current.clear();

    vehicles.forEach((v) => {
      const color = STATUS_COLOR[v.status] ?? "#64748b";

      const el = document.createElement("div");
      el.style.cssText = "width:14px;height:14px;cursor:pointer;";

      const dot = document.createElement("div");
      dot.style.cssText = `
        width:14px;height:14px;border-radius:50%;
        background:${color};
        border:2px solid white;
        box-shadow:0 2px 6px rgba(0,0,0,0.35);
        transition:transform 0.15s;
        transform-origin:center center;
      `;
      el.appendChild(dot);

      el.addEventListener("mouseenter", () => {
        dot.style.transform = "scale(1.7)";
        const { x, y } = map.project([v.lng, v.lat]);
        setHovered({ vehicle: v, x, y });
      });
      el.addEventListener("mouseleave", () => {
        dot.style.transform = "scale(1)";
        setHovered(null);
      });

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([v.lng, v.lat])
        .addTo(map);

      markersRef.current.set(v.id, { marker, dot, vehicle: v });
    });

    map.on("move", () => setHovered(null));
  // vehicles identity is stable per render — deps tracks length as a proxy
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [vehicles]);

  function flyToVehicle(v: VehiclePin) {
    setSelected(v);
    setQuery(v.licensePlate);
    setDropdown(false);
    setHovered(null);
    mapRef.current?.flyTo({ center: [v.lng, v.lat], zoom: 14, duration: 900, essential: true });
    markersRef.current.forEach(({ dot, vehicle }) => {
      dot.style.transform = vehicle.id === v.id ? "scale(2.2)" : "scale(1)";
    });
  }

  function clearSelection() {
    setSelected(null);
    setQuery("");
    markersRef.current.forEach(({ dot }) => { dot.style.transform = "scale(1)"; });
  }

  return (
    <MapBase
      height={height}
      deps={[vehicles.length]}
      onLoad={handleLoad}
    >
      {/* Search */}
      <div className="absolute top-3 left-3 z-10 w-64">
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => { setQuery(e.target.value); setDropdown(true); setSelected(null); }}
            onFocus={() => setDropdown(true)}
            onBlur={() => setTimeout(() => setDropdown(false), 150)}
            placeholder="Search trucks…"
            className="w-full rounded-lg border border-border bg-white/95 py-2 pl-8 pr-8 text-sm shadow-md outline-none focus:ring-2 focus:ring-primary/40"
          />
          {query && (
            <button onClick={clearSelection} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground">
              <X className="h-3.5 w-3.5" />
            </button>
          )}
        </div>

        {dropdownOpen && suggestions.length > 0 && (
          <div className="mt-1 overflow-hidden rounded-lg border border-border bg-white shadow-lg">
            {suggestions.slice(0, 6).map((v) => (
              <button
                key={v.id}
                onMouseDown={() => flyToVehicle(v)}
                className="flex w-full items-center gap-3 px-3 py-2.5 text-left text-sm transition-colors hover:bg-muted"
              >
                <span className="h-2 w-2 shrink-0 rounded-full" style={{ background: STATUS_COLOR[v.status] ?? "#64748b" }} />
                <span className="font-medium">{v.licensePlate}</span>
                <span className="truncate text-xs text-muted-foreground">{v.model}</span>
              </button>
            ))}
          </div>
        )}

        {dropdownOpen && query.trim() && suggestions.length === 0 && (
          <div className="mt-1 rounded-lg border border-border bg-white px-3 py-2.5 text-sm text-muted-foreground shadow-lg">
            No trucks match &ldquo;{query}&rdquo;
          </div>
        )}
      </div>

      {/* Hover tooltip */}
      {hovered && (
        <div
          className="absolute z-20 pointer-events-none"
          style={{ left: hovered.x + 18, top: hovered.y - 50, transform: "translateY(-50%)" }}
        >
          <VehicleCardMini
            licensePlate={hovered.vehicle.licensePlate}
            model={hovered.vehicle.model}
            status={hovered.vehicle.status}
            imageIndex={hovered.vehicle.imageIndex}
            fuelLevel={hovered.vehicle.fuelLevel}
            hasOpenMaintenance={hovered.vehicle.hasOpenMaintenance}
          />
        </div>
      )}

      {/* Selected panel */}
      {selected && !hovered && (
        <div className="absolute right-12 top-3 z-10">
          <div className="relative">
            <button
              onClick={clearSelection}
              className="absolute -top-2 -right-2 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-white shadow-md text-muted-foreground hover:text-foreground"
            >
              <X className="h-3 w-3" />
            </button>
            <VehicleCardMini
              licensePlate={selected.licensePlate}
              model={selected.model}
              status={selected.status}
              imageIndex={selected.imageIndex}
              fuelLevel={selected.fuelLevel}
              hasOpenMaintenance={selected.hasOpenMaintenance}
            />
          </div>
        </div>
      )}
    </MapBase>
  );
}
