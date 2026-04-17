"use client";

import { Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend);

type Props = {
  active: number;
  inactive: number;
  inMaintenance: number;
};

export function VehicleStatusChart({ active, inactive, inMaintenance }: Props) {
  const data = {
    labels: ["Active", "Inactive", "In Maintenance"],
    datasets: [
      {
        data: [active, inactive, inMaintenance],
        backgroundColor: [
          "rgba(34, 197, 94, 0.8)",
          "rgba(100, 116, 139, 0.8)",
          "rgba(239, 68, 68, 0.8)",
        ],
        borderColor: [
          "rgba(34, 197, 94, 1)",
          "rgba(100, 116, 139, 1)",
          "rgba(239, 68, 68, 1)",
        ],
        borderWidth: 2,
      },
    ],
  };

  return (
    <div style={{ height: "220px", position: "relative" }}>
      <Doughnut
        data={data}
        options={{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: "bottom",
              labels: { color: "rgba(255,255,255,0.7)", padding: 12, font: { size: 11 } },
            },
            tooltip: { enabled: true },
          },
        }}
      />
    </div>
  );
}
