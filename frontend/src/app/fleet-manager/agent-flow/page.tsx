"use client";

import { useState } from "react";
import { Pause, Play, RefreshCw } from "lucide-react";
import dynamic from "next/dynamic";

const AgentFlowCanvas = dynamic(
  () => import("@/components/agent-flow/AgentFlowCanvas").then((m) => m.AgentFlowCanvas),
  { ssr: false }
);

const LEGEND = [
  { status: "idle",    colour: "#9ca3af", label: "Idle" },
  { status: "running", colour: "#d97706", label: "Running" },
  { status: "success", colour: "#16a34a", label: "Success" },
  { status: "warning", colour: "#ea580c", label: "Warning" },
  { status: "error",   colour: "#dc2626", label: "Error" },
] as const;

const TYPE_LEGEND = [
  { colour: "#3b82f6", label: "Source" },
  { colour: "#8b5cf6", label: "Tool Gateway" },
  { colour: "#6366f1", label: "Agent" },
  { colour: "#f59e0b", label: "Queue" },
  { colour: "#22c55e", label: "Output" },
] as const;

export default function AgentFlowPage() {
  const [simulating, setSimulating] = useState(true);
  const [key, setKey] = useState(0);

  return (
    <div className="flex h-screen flex-col bg-white text-[#111827]">
      {/* ── Top bar ─────────────────────────────────────────────── */}
      <div className="flex items-center justify-between border-b border-[#e5e7eb] bg-white px-6 py-3">
        <div>
          <h1 className="text-base font-bold tracking-tight text-[#111827]">
            Agent Dataflow
          </h1>
          <p className="mt-0.5 text-[11px] text-[#6b7280]">
            Live view of the TraceData multi-agent pipeline
          </p>
        </div>

        {/* Legend chips */}
        <div className="hidden items-center gap-6 md:flex">
          <div className="flex items-center gap-3">
            {LEGEND.map(({ status, colour, label }) => (
              <span key={status} className="flex items-center gap-1.5 text-[10px] text-[#6b7280]">
                <span className="inline-block h-2 w-2 rounded-full" style={{ backgroundColor: colour }} />
                {label}
              </span>
            ))}
          </div>
          <div className="h-4 w-px bg-[#e5e7eb]" />
          <div className="flex items-center gap-3">
            {TYPE_LEGEND.map(({ colour, label }) => (
              <span key={label} className="flex items-center gap-1.5 text-[10px] text-[#6b7280]">
                <span className="inline-block h-3 w-1 rounded-sm" style={{ backgroundColor: colour }} />
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setKey((k) => k + 1)}
            className="flex items-center gap-1.5 rounded-md border border-[#e5e7eb] bg-white px-3 py-1.5 text-[11px] font-medium text-[#6b7280] transition hover:border-[#d1d5db] hover:bg-[#f9fafb] hover:text-[#111827]"
          >
            <RefreshCw className="h-3 w-3" />
            Reset
          </button>
          <button
            onClick={() => setSimulating((s) => !s)}
            className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[11px] font-medium transition ${
              simulating
                ? "border-[#fde68a] bg-[#fef3c7] text-[#d97706] hover:bg-[#fde68a]"
                : "border-[#bbf7d0] bg-[#dcfce7] text-[#16a34a] hover:bg-[#bbf7d0]"
            }`}
          >
            {simulating ? (
              <><Pause className="h-3 w-3" /> Pause</>
            ) : (
              <><Play className="h-3 w-3" /> Simulate</>
            )}
          </button>
        </div>
      </div>

      {/* ── Workflow header (GitHub Actions style) ─────────────── */}
      <div className="flex items-center gap-3 border-b border-[#e5e7eb] bg-[#f9fafb] px-6 py-2">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-[#9ca3af]">
          tracedata-platform
        </span>
        <span className="text-[#d1d5db]">/</span>
        <span className="text-[10px] font-semibold uppercase tracking-widest text-[#6366f1]">
          agent-pipeline.workflow
        </span>
        <span className="ml-auto flex items-center gap-1.5 text-[10px] text-[#9ca3af]">
          <span className={`inline-block h-1.5 w-1.5 rounded-full ${simulating ? "animate-pulse bg-[#f59e0b]" : "bg-[#d1d5db]"}`} />
          {simulating ? "Simulation active" : "Paused"}
        </span>
      </div>

      {/* ── Canvas ──────────────────────────────────────────────── */}
      <div className="flex-1 p-4 bg-[#f9fafb]">
        <AgentFlowCanvas key={key} simulating={simulating} />
      </div>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <div className="border-t border-[#e5e7eb] bg-white px-6 py-2">
        <p className="text-[10px] text-[#9ca3af]">
          Frontend-only placeholder · No live backend connection · Statuses are simulated
        </p>
      </div>
    </div>
  );
}
