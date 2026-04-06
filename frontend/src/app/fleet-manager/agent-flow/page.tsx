"use client";

import { useState } from "react";
import { Pause, Play, RefreshCw } from "lucide-react";
import dynamic from "next/dynamic";
import type { AgentNodeInspectDetails } from "@/components/agent-flow/AgentFlowCanvas";

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
  const [live, setLive] = useState(true);
  const [connection, setConnection] = useState<"connected" | "offline">("offline");
  const [key, setKey] = useState(0);
  const [selectedNode, setSelectedNode] = useState<AgentNodeInspectDetails | null>(null);

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
            onClick={() => {
              setSelectedNode(null);
              setKey((k) => k + 1);
            }}
            className="flex items-center gap-1.5 rounded-md border border-[#e5e7eb] bg-white px-3 py-1.5 text-[11px] font-medium text-[#6b7280] transition hover:border-[#d1d5db] hover:bg-[#f9fafb] hover:text-[#111827]"
          >
            <RefreshCw className="h-3 w-3" />
            Reset
          </button>
          <button
            onClick={() => setLive((s) => !s)}
            className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[11px] font-medium transition ${
              live
                ? "border-[#fde68a] bg-[#fef3c7] text-[#d97706] hover:bg-[#fde68a]"
                : "border-[#bbf7d0] bg-[#dcfce7] text-[#16a34a] hover:bg-[#bbf7d0]"
            }`}
          >
            {live ? (
              <><Pause className="h-3 w-3" /> Pause</>
            ) : (
              <><Play className="h-3 w-3" /> Live</>
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
          <span
            className={`inline-block h-1.5 w-1.5 rounded-full ${
              live && connection === "connected"
                ? "animate-pulse bg-[#22c55e]"
                : live
                  ? "animate-pulse bg-[#f59e0b]"
                  : "bg-[#d1d5db]"
            }`}
          />
          {live ? (connection === "connected" ? "Live connected" : "Reconnecting...") : "Paused"}
        </span>
      </div>

      {/* ── Canvas ──────────────────────────────────────────────── */}
      <div className="flex-1 p-4 bg-[#f9fafb]">
        <div className="h-full grid grid-cols-1 gap-4 lg:grid-cols-[1fr_320px]">
          <AgentFlowCanvas
            key={key}
            live={live}
            onConnectionChange={setConnection}
            onNodeInspect={setSelectedNode}
          />

          <aside className="rounded-xl border border-[#e5e7eb] bg-white p-4 shadow-sm">
            {!selectedNode ? (
              <div className="text-[11px] text-[#9ca3af]">
                Click a node to inspect its latest status and events.
              </div>
            ) : (
              <div className="flex h-full flex-col gap-3">
                <div>
                  <h2 className="text-sm font-semibold text-[#111827]">{selectedNode.label}</h2>
                  <p className="text-[10px] uppercase tracking-wide text-[#9ca3af]">
                    Agent: {selectedNode.agent}
                  </p>
                </div>
                <div className="rounded-md bg-[#f9fafb] p-2 text-[11px] text-[#374151]">
                  <div>Status: <span className="font-semibold">{selectedNode.status}</span></div>
                  <div>Worker health: <span className="font-semibold">{selectedNode.workerHealth ?? "n/a"}</span></div>
                  <div>Trip: <span className="font-semibold">{selectedNode.tripId ?? "n/a"}</span></div>
                </div>
                <div className="min-h-0 flex-1">
                  <p className="mb-2 text-[11px] font-semibold text-[#374151]">Recent events</p>
                  <div className="max-h-full overflow-auto space-y-2 pr-1">
                    {selectedNode.events.length === 0 ? (
                      <p className="text-[11px] text-[#9ca3af]">No events yet for this node.</p>
                    ) : (
                      selectedNode.events.map((event, idx) => (
                        <div key={`${event.seq}-${idx}`} className="rounded-md border border-[#e5e7eb] p-2">
                          <div className="text-[10px] text-[#6b7280]">
                            {new Date(event.ts).toLocaleTimeString()}
                          </div>
                          <div className="text-[11px] text-[#111827]">
                            {event.event_type} · <span className="font-semibold">{event.status}</span>
                          </div>
                          {event.trip_id && (
                            <div className="text-[10px] text-[#6b7280]">trip: {event.trip_id}</div>
                          )}
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            )}
          </aside>
        </div>
      </div>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <div className="border-t border-[#e5e7eb] bg-white px-6 py-2">
        <p className="text-[10px] text-[#9ca3af]">
          Real-time view via SSE · Event stream: /api/v1/agent-flow/stream
        </p>
      </div>
    </div>
  );
}
