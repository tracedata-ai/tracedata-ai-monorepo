"use client";

import { useEffect, useState } from "react";

type WeatherData = {
  temp: number;
  feelsLike: number;
  description: string;
  icon: string;
  windSpeed: number;
  windDeg: number;
  humidity: number;
  visibility: number;   // metres
  rain1h: number | null;
};

type AqiData = {
  aqi: number;
  pm25: number;
};

const AQI_LABEL: Record<number, { label: string; color: string }> = {
  1: { label: "Good",      color: "#22c55e" },
  2: { label: "Fair",      color: "#84cc16" },
  3: { label: "Moderate",  color: "#fbbf24" },
  4: { label: "Poor",      color: "#f97316" },
  5: { label: "Very Poor", color: "#dc2626" },
};

function windDir(deg: number): string {
  const dirs = ["N","NE","E","SE","S","SW","W","NW"];
  return dirs[Math.round(deg / 45) % 8];
}

async function fetchWeather(lat: number, lon: number, key: string): Promise<WeatherData | null> {
  try {
    const r = await fetch(
      `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${key}&units=metric`
    );
    const d = await r.json();
    return {
      temp:        Math.round(d.main.temp),
      feelsLike:   Math.round(d.main.feels_like),
      description: d.weather[0]?.description ?? "",
      icon:        d.weather[0]?.icon ?? "",
      windSpeed:   Math.round(d.wind.speed * 3.6), // m/s → km/h
      windDeg:     d.wind.deg ?? 0,
      humidity:    d.main.humidity,
      visibility:  d.visibility ?? 0,
      rain1h:      d.rain?.["1h"] ?? null,
    };
  } catch {
    return null;
  }
}

async function fetchAqi(lat: number, lon: number, key: string): Promise<AqiData | null> {
  try {
    const r = await fetch(
      `https://api.openweathermap.org/data/2.5/air_pollution?lat=${lat}&lon=${lon}&appid=${key}`
    );
    const d = await r.json();
    const item = d.list?.[0];
    return item ? { aqi: item.main.aqi, pm25: Math.round(item.components.pm2_5) } : null;
  } catch {
    return null;
  }
}

type Props = {
  lat?: number;
  lon?: number;
};

export function WeatherWidget({ lat = 1.35, lon = 103.82 }: Props) {
  const key = process.env.NEXT_PUBLIC_OWM_TOKEN ?? "";
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [aqi,     setAqi]     = useState<AqiData | null>(null);

  useEffect(() => {
    if (!key) return;

    function load() {
      fetchWeather(lat, lon, key).then(setWeather);
      fetchAqi(lat, lon, key).then(setAqi);
    }

    load();
    const id = setInterval(load, 10 * 60 * 1000); // refresh every 10 min
    return () => clearInterval(id);
  }, [lat, lon, key]);

  if (!key || !weather) return null;

  const aqiInfo = aqi ? AQI_LABEL[aqi.aqi] : null;
  const visKm   = (weather.visibility / 1000).toFixed(1);

  return (
    <div className="absolute top-3 right-3 z-10 flex items-center gap-2 rounded-xl bg-black/65 px-3 py-2 backdrop-blur-sm text-white">
      {/* Icon + temp */}
      <div className="flex items-center gap-1.5">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={`https://openweathermap.org/img/wn/${weather.icon}.png`}
          alt={weather.description}
          width={28}
          height={28}
          className="-my-1"
        />
        <div className="leading-tight">
          <span className="text-sm font-bold">{weather.temp}°C</span>
          <span className="ml-1 text-[10px] text-white/60">feels {weather.feelsLike}°</span>
        </div>
      </div>

      <div className="h-4 w-px bg-white/20" />

      {/* Wind */}
      <div className="flex items-center gap-1 text-[11px]">
        <span className="text-white/50">💨</span>
        <span>{weather.windSpeed} km/h {windDir(weather.windDeg)}</span>
      </div>

      <div className="h-4 w-px bg-white/20" />

      {/* Visibility */}
      <div className="flex items-center gap-1 text-[11px]">
        <span className="text-white/50">👁</span>
        <span>{visKm} km</span>
      </div>

      <div className="h-4 w-px bg-white/20" />

      {/* Humidity / rain */}
      <div className="flex items-center gap-1 text-[11px]">
        <span className="text-white/50">💧</span>
        <span>
          {weather.rain1h != null
            ? `${weather.rain1h.toFixed(1)} mm/h`
            : `${weather.humidity}%`}
        </span>
      </div>

      {/* AQI */}
      {aqiInfo && (
        <>
          <div className="h-4 w-px bg-white/20" />
          <div className="flex items-center gap-1 text-[11px]">
            <span className="text-white/50">AQI</span>
            <span className="font-semibold" style={{ color: aqiInfo.color }}>
              {aqiInfo.label}
            </span>
          </div>
        </>
      )}
    </div>
  );
}
