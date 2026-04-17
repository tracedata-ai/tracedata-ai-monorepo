"use client";

import { useEffect, useRef } from "react";

type Props = {
  height?: number;
  mapStyle?: string;
  center?: [number, number];
  zoom?: number;
  minZoom?: number;
  /** Called once when the map's 'load' event fires. Return a cleanup fn if needed. */
  onLoad: (map: any, mapboxgl: any) => (() => void) | void;
  /** Extra deps that should retrigger map initialization (e.g. data length). */
  deps?: unknown[];
  /** Overlays rendered on top of the canvas (search bar, legend, etc.). */
  children?: React.ReactNode;
  /** If true, show a "no data" message instead of initializing the map. */
  empty?: boolean;
  emptyMessage?: string;
};

export function MapBase({
  height = 400,
  mapStyle = "mapbox://styles/mapbox/streets-v12",
  center = [103.82, 1.35],
  zoom = 11,
  minZoom = 9,
  onLoad,
  deps = [],
  children,
  empty = false,
  emptyMessage = "No data to display.",
}: Props) {
  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN;

  const outerRef     = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  // Store the latest onLoad in a ref so stale-closure issues don't force map re-init
  const onLoadRef = useRef(onLoad);
  useEffect(() => { onLoadRef.current = onLoad; });

  useEffect(() => {
    if (!token || !containerRef.current || empty) return;

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let map: any;
    let userCleanup: (() => void) | void;

    async function init() {
      try {
        const mapboxgl = (await import("mapbox-gl")).default;
        await import("mapbox-gl/dist/mapbox-gl.css");
        if (!containerRef.current) return;

        mapboxgl.accessToken = token!;
        map = new mapboxgl.Map({
          container: containerRef.current,
          style: mapStyle,
          center,
          zoom,
          minZoom,
        });

        map.addControl(new mapboxgl.NavigationControl(), "top-right");
        map.addControl(
          new mapboxgl.FullscreenControl({ container: outerRef.current ?? undefined }),
          "top-right"
        );

        map.on("load", () => {
          userCleanup = onLoadRef.current(map, mapboxgl);
        });
      } catch (err) {
        console.error("[MapBase] init failed:", err);
      }
    }

    init();

    return () => {
      userCleanup?.();
      map?.remove();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, mapStyle, empty, ...deps]);

  if (!token) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-border bg-muted text-sm text-muted-foreground"
        style={{ height }}
      >
        Set{" "}
        <code className="mx-1 rounded bg-muted-foreground/10 px-1 font-mono text-xs">
          NEXT_PUBLIC_MAPBOX_TOKEN
        </code>{" "}
        to enable the map.
      </div>
    );
  }

  if (empty) {
    return (
      <div
        className="flex items-center justify-center rounded-xl border border-border bg-muted text-sm text-muted-foreground"
        style={{ height }}
      >
        {emptyMessage}
      </div>
    );
  }

  return (
    <div ref={outerRef} className="relative rounded-xl overflow-hidden" style={{ height }}>
      <div ref={containerRef} className="h-full w-full" />
      {children}
    </div>
  );
}
