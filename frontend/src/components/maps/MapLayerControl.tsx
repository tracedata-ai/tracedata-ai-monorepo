"use client";

import { Layers } from "lucide-react";

type Props = {
  showTraffic: boolean;
  onTrafficToggle: () => void;
  showRain: boolean;
  onRainToggle: () => void;
  showTemp: boolean;
  onTempToggle: () => void;
  hasOWM?: boolean;
};

export function MapLayerControl({
  showTraffic,
  onTrafficToggle,
  showRain,
  onRainToggle,
  showTemp,
  onTempToggle,
  hasOWM = false,
}: Props) {
  const owmBtn = (active: boolean, label: string, activeClass: string, onClick: () => void) => (
    <button
      onClick={onClick}
      disabled={!hasOWM}
      title={!hasOWM ? "Add NEXT_PUBLIC_OWM_TOKEN to .env.local" : undefined}
      className={`rounded px-2 py-0.5 text-[11px] font-semibold transition-colors ${
        !hasOWM
          ? "cursor-not-allowed text-white/30"
          : active
          ? `${activeClass} text-white`
          : "text-white/60 hover:text-white"
      }`}
    >
      {label}
    </button>
  );

  return (
    <div className="absolute bottom-8 left-3 z-10 flex flex-col gap-1.5">
      {/* Toggle pill */}
      <div className="flex items-center gap-1.5 rounded-lg bg-black/60 px-2.5 py-1.5 backdrop-blur-sm">
        <Layers className="h-3 w-3 shrink-0 text-white/60" />
        <button
          onClick={onTrafficToggle}
          className={`rounded px-2 py-0.5 text-[11px] font-semibold transition-colors ${
            showTraffic ? "bg-orange-500 text-white" : "text-white/60 hover:text-white"
          }`}
        >
          Traffic
        </button>
        <div className="h-3 w-px bg-white/20" />
        {owmBtn(showRain, "Rain",  "bg-blue-500", onRainToggle)}
        <div className="h-3 w-px bg-white/20" />
        {owmBtn(showTemp, "Temp",  "bg-rose-500", onTempToggle)}
      </div>

      {/* Traffic legend */}
      {showTraffic && (
        <div className="rounded-lg bg-black/60 px-2.5 py-1.5 backdrop-blur-sm">
          <p className="mb-1 text-[9px] font-bold uppercase tracking-widest text-white/50">Traffic</p>
          <div className="flex flex-col gap-0.5">
            {[
              { label: "Free flow", color: "#22c55e" },
              { label: "Moderate",  color: "#fbbf24" },
              { label: "Heavy",     color: "#f97316" },
              { label: "Severe",    color: "#dc2626" },
            ].map(({ label, color }) => (
              <div key={label} className="flex items-center gap-1.5">
                <span className="h-1.5 w-4 rounded-full" style={{ background: color }} />
                <span className="text-[9px] text-white/60">{label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
