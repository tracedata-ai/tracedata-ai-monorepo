"use client";

import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

type StatusCount = { label: string; count: number };

type Props = {
  statuses: StatusCount[];
};

export function TripStatusChart({ statuses }: Props) {
  const palette = [
    "rgba(59, 130, 246, 0.8)",
    "rgba(34, 197, 94, 0.8)",
    "rgba(239, 68, 68, 0.8)",
    "rgba(251, 191, 36, 0.8)",
    "rgba(168, 85, 247, 0.8)",
  ];

  const data = {
    labels: statuses.map((s) => s.label),
    datasets: [
      {
        label: "Trips",
        data: statuses.map((s) => s.count),
        backgroundColor: statuses.map((_, i) => palette[i % palette.length]),
        borderRadius: 6,
        borderSkipped: false,
      },
    ],
  };

  return (
    <div style={{ height: "220px", position: "relative" }}>
      <Bar
        data={data}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: {
              ticks: { color: "rgba(255,255,255,0.6)", font: { size: 11 } },
              grid: { color: "rgba(255,255,255,0.05)" },
            },
            y: {
              beginAtZero: true,
              ticks: { color: "rgba(255,255,255,0.6)", font: { size: 11 } },
              grid: { color: "rgba(255,255,255,0.05)" },
            },
          },
        }}
      />
    </div>
  );
}
