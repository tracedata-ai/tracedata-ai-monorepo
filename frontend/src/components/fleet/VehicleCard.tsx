"use client";

import Image from "next/image";

const VEHICLES: { src: string; type: string; gradient: string }[] = [
  {
    src:      "/img/ford-transit-panel-van.png",
    type:     "Panel Van",
    gradient: "from-orange-500 via-orange-700 to-red-900",
  },
  {
    src:      "/img/sprinter-panel-van.png",
    type:     "Sprinter Van",
    gradient: "from-blue-400 via-blue-600 to-blue-900",
  },
  {
    src:      "/img/vauxhall-combo.png",
    type:     "Combo Van",
    gradient: "from-violet-500 via-purple-700 to-indigo-900",
  },
  {
    src:      "/img/ford-ranger-pickup.png",
    type:     "Pickup Truck",
    gradient: "from-teal-400 via-teal-600 to-emerald-900",
  },
  {
    src:      "/img/ford-transit-minibus-19-seater.png",
    type:     "Minibus",
    gradient: "from-rose-400 via-rose-600 to-pink-900",
  },
  {
    src:      "/img/ford-transit-e-custome.png",
    type:     "E-Custom Van",
    gradient: "from-sky-400 via-indigo-600 to-violet-900",
  },
];

const STATUS_DOT: Record<string, string> = {
  active:         "bg-green-400",
  in_maintenance: "bg-red-400",
  inactive:       "bg-slate-400",
};

type Props = {
  id: string;
  licensePlate: string;
  model: string;
  status: string;
  imageIndex: number;
  onClick?: () => void;
};

export function VehicleCard({ id, licensePlate, model, status, imageIndex, onClick }: Props) {
  const v = VEHICLES[imageIndex % VEHICLES.length];

  return (
    <div
      onClick={onClick}
      className={`shimmer-card group cursor-pointer rounded-2xl bg-linear-to-br ${v.gradient} p-5 flex flex-col justify-between min-h-75 shadow-lg hover:shadow-2xl hover:-translate-y-1 transition-all duration-300`}
    >
      {/* ── Top: vehicle image ── */}
      <div className="relative h-36 w-full mb-3">
        <Image
          src={v.src}
          alt={v.type}
          fill
          className="object-contain object-center drop-shadow-xl transition-transform duration-500 group-hover:scale-105"
          priority={imageIndex < 6}
        />
      </div>

      {/* ── Middle: type tag + name ── */}
      <div className="space-y-1 z-10 relative flex-1">
        <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-white/60">
          {v.type}
        </p>
        <p className="text-xl font-black tracking-tight text-white leading-tight">
          {model}
        </p>
        <p className="text-xs font-semibold text-white/70 font-mono">{licensePlate}</p>
      </div>

      {/* ── Bottom: status ── */}
      <div className="relative z-10 flex items-center justify-between mt-3">
        <div className="flex items-center gap-2">
          <span className={`h-2 w-2 rounded-full ${STATUS_DOT[status] ?? "bg-slate-400"} shadow-sm`} />
          <span className="text-xs font-semibold text-white/80 capitalize">
            {status.replace(/_/g, " ")}
          </span>
        </div>
        <span className="font-mono text-[10px] text-white/40">{id}</span>
      </div>
    </div>
  );
}
