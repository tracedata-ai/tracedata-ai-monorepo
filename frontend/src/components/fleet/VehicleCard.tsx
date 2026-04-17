"use client";

import Image from "next/image";
import { Badge } from "@/components/ui/badge";

const VEHICLE_IMAGES: { src: string; type: string }[] = [
  { src: "/img/ford-transit-panel-van.png",        type: "Panel Van" },
  { src: "/img/sprinter-panel-van.png",            type: "Sprinter Van" },
  { src: "/img/vauxhall-combo.png",                type: "Combo Van" },
  { src: "/img/ford-ranger-pickup.png",            type: "Pickup Truck" },
  { src: "/img/ford-transit-minibus-19-seater.png",type: "Minibus" },
  { src: "/img/ford-transit-e-custome.png",        type: "E-Custom Van" },
];

const STATUS_STYLE: Record<string, string> = {
  active:         "bg-green-600",
  in_maintenance: "bg-red-500",
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
  const img = VEHICLE_IMAGES[imageIndex % VEHICLE_IMAGES.length];

  return (
    <div
      onClick={onClick}
      className="group rounded-xl border border-border bg-card overflow-hidden shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer hover:-translate-y-0.5"
    >
      {/* Vehicle image */}
      <div className="relative flex items-center justify-center h-44 bg-gradient-to-br from-slate-50 to-slate-100 px-6">
        <Image
          src={img.src}
          alt={img.type}
          width={240}
          height={150}
          className="object-contain drop-shadow-md transition-transform duration-300 group-hover:scale-[1.04]"
          priority={imageIndex < 6}
        />
        <Badge
          className={`absolute top-3 right-3 ${STATUS_STYLE[status] ?? "bg-slate-400"} text-white text-[10px] capitalize`}
        >
          {status.replace(/_/g, " ")}
        </Badge>
      </div>

      {/* Info */}
      <div className="border-t border-border px-4 py-3 space-y-0.5">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
          {img.type}
        </p>
        <p className="text-base font-bold tracking-tight">{licensePlate}</p>
        <p className="text-sm text-muted-foreground">{model}</p>
        <p className="pt-1 font-mono text-[10px] text-muted-foreground/50">{id}</p>
      </div>
    </div>
  );
}
