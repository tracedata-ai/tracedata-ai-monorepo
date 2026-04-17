"use client";

import Image from "next/image";

type VehicleStyling = {
  brand:      string;
  background: string;
};

const VEHICLES: { src: string; type: string; styling: VehicleStyling }[] = [
  {
    src:     "/img/ford-transit-panel-van.png",
    type:    "Panel Van",
    styling: { brand: "text-orange-600 bg-gray-200", background: "bg-blend-overlay bg-orange-800/70" },
  },
  {
    src:     "/img/sprinter-panel-van.png",
    type:    "Sprinter Van",
    styling: { brand: "text-blue-600 bg-gray-200", background: "bg-blend-overlay bg-blue-900/80" },
  },
  {
    src:     "/img/vauxhall-combo.png",
    type:    "Combo Van",
    styling: { brand: "text-violet-600 bg-gray-200", background: "bg-blend-overlay bg-violet-900/80" },
  },
  {
    src:     "/img/ford-ranger-pickup.png",
    type:    "Pickup Truck",
    styling: { brand: "text-teal-700 bg-gray-200", background: "bg-blend-overlay bg-teal-900/80" },
  },
  {
    src:     "/img/ford-transit-minibus-19-seater.png",
    type:    "Minibus",
    styling: { brand: "text-rose-600 bg-gray-200", background: "bg-blend-overlay bg-rose-900/80" },
  },
  {
    src:     "/img/ford-transit-e-custome.png",
    type:    "E-Custom Van",
    styling: { brand: "text-sky-600 bg-gray-200", background: "bg-blend-overlay bg-sky-900/80" },
  },
];

const STATUS_DOT: Record<string, string> = {
  active:         "bg-green-400",
  in_maintenance: "bg-red-400",
  inactive:       "bg-slate-400",
};

type Props = {
  id?: string;
  licensePlate: string;
  model: string;
  status: string;
  imageIndex: number;
  onClick?: () => void;
};

export function VehicleCard({ licensePlate, model, status, imageIndex, onClick }: Props) {
  const v = VEHICLES[imageIndex % VEHICLES.length];

  return (
    <div
      onClick={onClick}
      className="group relative aspect-3/4 w-full cursor-pointer overflow-hidden rounded-xl shadow-lg transition-all duration-300 hover:-translate-y-2 hover:scale-102 hover:shadow-2xl"
    >
      {/* ── Layered gradient background ── */}
      <div
        className={`absolute inset-0 bg-linear-to-b ${v.styling.background} from-30% via-gray-300 via-60% to-gray-800 to-95%`}
      >
        <div className="absolute inset-0 bg-linear-to-r from-blue-600/0 via-slate-600/10 to-indigo-600/0 opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
      </div>

      {/* ── Content ── */}
      <div className="relative z-10 flex h-full flex-col p-5">

        {/* Header: model name + type badge */}
        <div className="flex items-start justify-between gap-2">
          <h2 className="font-semibold leading-tight text-white transition-colors group-hover:text-blue-200"
              style={{ fontSize: "clamp(0.9rem, 2.5vw, 1.25rem)" }}>
            {model}
          </h2>
          <span className={`shrink-0 rounded-md bg-black/20 px-2 py-0.5 text-[10px] font-bold backdrop-blur-sm shadow-md ${v.styling.brand}`}>
            {v.type}
          </span>
        </div>

        {/* Status row */}
        <div className="mt-1.5 flex items-center gap-1.5 text-gray-300 group-hover:text-white transition-colors">
          <span className={`h-2 w-2 rounded-full ${STATUS_DOT[status] ?? "bg-slate-400"}`} />
          <span className="text-xs font-medium capitalize">{status.replace(/_/g, " ")}</span>
        </div>

        {/* Vehicle image */}
        <div className="relative my-3 flex flex-1 items-center justify-center">
          <div className="relative h-40 w-full">
            <Image
              src={v.src}
              alt={v.type}
              fill
              className="object-contain drop-shadow-lg transition-transform duration-500 group-hover:scale-110"
              priority={imageIndex < 6}
            />
            {/* Image-level shimmer sweep */}
            <div className="absolute inset-0 -translate-x-full bg-linear-to-r from-transparent via-white/30 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
          </div>
        </div>

        {/* Bottom: license plate + animated underline */}
        <div className="relative mt-auto">
          <div className="inline-flex items-center rounded-md border-2 border-black bg-white px-2.5 py-0.5 shadow-md">
            <span className="font-mono text-xs font-black tracking-widest text-black uppercase">
              {licensePlate}
            </span>
          </div>
          <div className="absolute -bottom-5 left-0 h-0.5 w-0 bg-linear-to-r from-blue-400 to-purple-400 transition-all duration-500 group-hover:w-full" />
        </div>
      </div>

      {/* Hover ring */}
      <div className="absolute inset-0 rounded-xl ring-0 ring-blue-400/0 transition-all duration-300 group-hover:ring-2 group-hover:ring-blue-400/50" />
    </div>
  );
}
