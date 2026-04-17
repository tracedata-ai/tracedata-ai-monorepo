"use client";

import { useEffect, useRef } from "react";

type VehiclePin = {
  id: string;
  licensePlate: string;
  status: string;
  lat: number;
  lng: number;
};

type Props = {
  vehicles: VehiclePin[];
  height?: number;
};

const STATUS_COLOR: Record<string, string> = {
  active: "#22c55e",
  in_maintenance: "#ef4444",
  inactive: "#64748b",
};

/**
 * Requires NEXT_PUBLIC_MAPBOX_TOKEN in your .env.local.
 * Vehicles need lat/lng — pass mock coordinates when the backend doesn't supply them.
 */
export function FleetMap({ vehicles, height = 360 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<import("mapbox-gl").Map | null>(null);

  useEffect(() => {
    const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
    if (!token || !containerRef.current || mapRef.current) return;

    let map: import("mapbox-gl").Map;

    async function initMap() {
      const mapboxgl = (await import("mapbox-gl")).default;
      await import("mapbox-gl/dist/mapbox-gl.css");

      mapboxgl.accessToken = token!;

      map = new mapboxgl.Map({
        container: containerRef.current!,
        style: "mapbox://styles/mapbox/light-v11",
        center: [103.82, 1.35],
        zoom: 11,
      });

      map.addControl(new mapboxgl.NavigationControl(), "top-right");
      mapRef.current = map;

      map.on("load", () => {
        vehicles.forEach((v) => {
          const el = document.createElement("div");
          el.style.cssText = `
            width:14px;height:14px;border-radius:50%;
            background:${STATUS_COLOR[v.status] ?? "#64748b"};
            border:2px solid white;
            box-shadow:0 2px 6px rgba(0,0,0,0.5);
            cursor:pointer;
          `;

          const popup = new mapboxgl.Popup({ offset: 20, closeButton: false }).setHTML(
            `<div style="font-family:monospace;font-size:12px;line-height:1.5">
              <strong>${v.licensePlate}</strong><br/>
              ${v.status}
            </div>`,
          );

          new mapboxgl.Marker(el)
            .setLngLat([v.lng, v.lat])
            .setPopup(popup)
            .addTo(map);
        });
      });
    }

    initMap();

    return () => {
      map?.remove();
      mapRef.current = null;
    };
  }, [vehicles]);

  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;
  if (!token) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-white/10 bg-black/20 text-sm text-muted-foreground"
        style={{ height }}
      >
        Add <code className="mx-1 rounded bg-white/10 px-1 py-0.5 font-mono text-xs">NEXT_PUBLIC_MAPBOX_TOKEN</code> to{" "}
        <code className="mx-1 rounded bg-white/10 px-1 py-0.5 font-mono text-xs">.env.local</code> to enable the map.
      </div>
    );
  }

  return <div ref={containerRef} className="rounded-xl overflow-hidden" style={{ height }} />;
}
