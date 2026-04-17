"use client";

import { useState } from "react";
import { Pause, Play, RefreshCw, ExternalLink, ChevronDown, ChevronRight } from "lucide-react";
import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";
import type { AgentNodeInspectDetails } from "@/components/agent-flow/AgentFlowCanvas";
import type { AgentFlowEvent } from "@/lib/api";

const AgentFlowCanvas = dynamic(
  () => import("@/components/agent-flow/AgentFlowCanvas").then((m) => m.AgentFlowCanvas),
  { ssr: false }
);

// ── Helpers ───────────────────────────────────────────────────────────────────

const STATUS_DOT: Record<string, string> = {
  idle:    "#9ca3af",
  queued:  "#3b82f6",
  running: "#d97706",
  success: "#16a34a",
  error:   "#dc2626",
};

const STATUS_BG: Record<string, string> = {
  idle:    "bg-gray-100 text-gray-600",
  queued:  "bg-blue-50 text-blue-700",
  running: "bg-amber-50 text-amber-700",
  success: "bg-green-50 text-green-700",
  error:   "bg-red-50 text-red-700",
};

const HEALTH_DOT: Record<string, string> = {
  healthy:   "#16a34a",
  degraded:  "#d97706",
  unhealthy: "#dc2626",
};

const HEALTH_LABEL: Record<string, string> = {
  healthy:   "text-green-700",
  degraded:  "text-amber-700",
  unhealthy: "text-red-700",
};

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

// ── JSON viewer ───────────────────────────────────────────────────────────────

function JsonValue({ value }: { value: unknown }) {
  if (value === null) return <span className="text-gray-400">null</span>;
  if (typeof value === "boolean") return <span className="text-orange-500">{String(value)}</span>;
  if (typeof value === "number")  return <span className="text-blue-600">{value}</span>;
  if (typeof value === "string")  return <span className="text-green-700">&quot;{value}&quot;</span>;
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-gray-500">[]</span>;
    return (
      <span>
        {"["}
        <div className="pl-4">
          {value.map((v, i) => (
            <div key={i}>
              <JsonValue value={v} />{i < value.length - 1 ? "," : ""}
            </div>
          ))}
        </div>
        {"]"}
      </span>
    );
  }
  if (typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>);
    if (entries.length === 0) return <span className="text-gray-500">{"{}"}</span>;
    return (
      <span>
        {"{"}
        <div className="pl-4">
          {entries.map(([k, v], i) => (
            <div key={k}>
              <span className="text-[#111827] font-medium">&quot;{k}&quot;</span>
              <span className="text-gray-500">: </span>
              <JsonValue value={v} />{i < entries.length - 1 ? "," : ""}
            </div>
          ))}
        </div>
        {"}"}
      </span>
    );
  }
  return <span>{String(value)}</span>;
}

// ── Event card ────────────────────────────────────────────────────────────────

function EventCard({ event }: { event: AgentFlowEvent }) {
  const [open, setOpen] = useState(false);
  const hasMeta = event.meta && Object.keys(event.meta).length > 0;
  const payload: Record<string, unknown> = {
    event_type: event.event_type,
    status:     event.status,
    seq:        event.seq,
    ...(event.trip_id ? { trip_id: event.trip_id } : {}),
    ...(event.meta   ? event.meta : {}),
  };

  return (
    <div className="rounded-md border border-[#e5e7eb] bg-white text-[11px]">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-start gap-2 px-3 py-2 text-left hover:bg-[#f9fafb] transition-colors rounded-md"
      >
        {open
          ? <ChevronDown className="mt-0.5 h-3 w-3 shrink-0 text-[#9ca3af]" />
          : <ChevronRight className="mt-0.5 h-3 w-3 shrink-0 text-[#9ca3af]" />
        }
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-[#111827]">{event.event_type}</span>
            <span
              className={`rounded px-1.5 py-0.5 text-[9px] font-bold uppercase ${STATUS_BG[event.status] ?? "bg-gray-100 text-gray-500"}`}
            >
              {event.status}
            </span>
          </div>
          <div className="text-[10px] text-[#9ca3af]">
            {new Date(event.ts).toLocaleTimeString()} · seq {event.seq}
          </div>
          {event.trip_id && !open && (
            <div className="truncate text-[10px] text-[#6b7280]">trip: {event.trip_id}</div>
          )}
        </div>
      </button>

      {open && (
        <div className="border-t border-[#f3f4f6] px-3 py-2 font-mono text-[10px] leading-relaxed text-[#374151] overflow-auto max-h-64">
          <JsonValue value={payload} />
        </div>
      )}
    </div>
  );
}

// ── Inspector panel ───────────────────────────────────────────────────────────

function InspectorPanel({ node }: { node: AgentNodeInspectDetails }) {
  const router = useRouter();
  const statusColor = STATUS_DOT[node.status] ?? "#9ca3af";
  const healthColor = node.workerHealth ? HEALTH_DOT[node.workerHealth] : undefined;
  const healthLabel = node.workerHealth ? HEALTH_LABEL[node.workerHealth] : undefined;

  return (
    <div className="flex h-full flex-col gap-4 overflow-hidden">

      {/* Header */}
      <div>
        <h2 className="text-sm font-bold text-[#111827]">{node.label}</h2>
        <p className="text-[10px] uppercase tracking-wider text-[#9ca3af]">{node.agent}</p>
      </div>

      {/* Status + Health */}
      <div className="flex items-center gap-3">
        <div className={`flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase ${STATUS_BG[node.status] ?? "bg-gray-100 text-gray-500"}`}>
          <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: statusColor }} />
          {node.status}
        </div>
        {healthColor && (
          <div className={`flex items-center gap-1.5 text-[10px] font-semibold uppercase ${healthLabel}`}>
            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: healthColor }} />
            Worker {node.workerHealth}
          </div>
        )}
      </div>

      {/* Active trip */}
      {node.tripId && (
        <div className="rounded-md border border-[#e5e7eb] bg-[#f9fafb] px-3 py-2">
          <p className="text-[9px] font-semibold uppercase tracking-widest text-[#9ca3af]">Active Trip</p>
          <div className="mt-1 flex items-center gap-2">
            <span className="font-mono text-[10px] text-[#374151] truncate">{node.tripId}</span>
            <button
              onClick={() => router.push(`/fleet-manager/trips/${node.tripId}`)}
              className="shrink-0 text-[#6366f1] hover:text-[#4f46e5]"
            >
              <ExternalLink className="h-3 w-3" />
            </button>
          </div>
        </div>
      )}

      {/* Events list */}
      <div className="flex-1 min-h-0 flex flex-col gap-2 overflow-hidden">
        <p className="text-[10px] font-semibold uppercase tracking-widest text-[#9ca3af]">
          Recent Events ({node.events.length})
        </p>
        <div className="flex-1 overflow-y-auto space-y-1.5 pr-0.5">
          {node.events.length === 0 ? (
            <p className="text-[11px] text-[#9ca3af]">No events yet.</p>
          ) : (
            node.events.map((ev, i) => <EventCard key={`${ev.seq}-${i}`} event={ev} />)
          )}
        </div>
      </div>
    </div>
  );
}

// ── Page ──────────────────────────────────────────────────────────────────────

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
          <h1 className="text-base font-bold tracking-tight text-[#111827]">Agent Dataflow</h1>
          <p className="mt-0.5 text-[11px] text-[#6b7280]">
            Live view of the TraceData multi-agent pipeline
          </p>
        </div>

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

        <div className="flex items-center gap-2">
          <button
            onClick={() => { setSelectedNode(null); setKey((k) => k + 1); }}
            className="flex items-center gap-1.5 rounded-md border border-[#e5e7eb] bg-white px-3 py-1.5 text-[11px] font-medium text-[#6b7280] transition hover:border-[#d1d5db] hover:bg-[#f9fafb] hover:text-[#111827]"
          >
            <RefreshCw className="h-3 w-3" /> Reset
          </button>
          <button
            onClick={() => setLive((s) => !s)}
            className={`flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-[11px] font-medium transition ${
              live
                ? "border-[#fde68a] bg-[#fef3c7] text-[#d97706] hover:bg-[#fde68a]"
                : "border-[#bbf7d0] bg-[#dcfce7] text-[#16a34a] hover:bg-[#bbf7d0]"
            }`}
          >
            {live ? <><Pause className="h-3 w-3" /> Pause</> : <><Play className="h-3 w-3" /> Live</>}
          </button>
        </div>
      </div>

      {/* ── Workflow breadcrumb ─────────────────────────────────── */}
      <div className="flex items-center gap-3 border-b border-[#e5e7eb] bg-[#f9fafb] px-6 py-2">
        <span className="text-[10px] font-semibold uppercase tracking-widest text-[#9ca3af]">
          tracedata-platform
        </span>
        <span className="text-[#d1d5db]">/</span>
        <span className="text-[10px] font-semibold uppercase tracking-widest text-[#6366f1]">
          agent-pipeline.workflow
        </span>
        <span className="ml-auto flex items-center gap-1.5 text-[10px] text-[#9ca3af]">
          <span className={`inline-block h-1.5 w-1.5 rounded-full ${
            live && connection === "connected"
              ? "animate-pulse bg-[#22c55e]"
              : live ? "animate-pulse bg-[#f59e0b]"
              : "bg-[#d1d5db]"
          }`} />
          {live ? (connection === "connected" ? "Live connected" : "Reconnecting…") : "Paused"}
        </span>
      </div>

      {/* ── Canvas + Inspector ──────────────────────────────────── */}
      <div className="flex-1 overflow-hidden p-4 bg-[#f9fafb]">
        <div className="h-full grid grid-cols-1 gap-4 lg:grid-cols-[1fr_340px]">
          <AgentFlowCanvas
            key={key}
            live={live}
            onConnectionChange={setConnection}
            onNodeInspect={setSelectedNode}
          />

          <aside className="rounded-xl border border-[#e5e7eb] bg-white p-4 shadow-sm overflow-hidden flex flex-col">
            {!selectedNode ? (
              <div className="flex h-full items-center justify-center">
                <p className="text-center text-[11px] text-[#9ca3af]">
                  Click any agent node to inspect its status, worker health, and live event payloads.
                </p>
              </div>
            ) : (
              <InspectorPanel node={selectedNode} />
            )}
          </aside>
        </div>
      </div>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <div className="border-t border-[#e5e7eb] bg-white px-6 py-2">
        <p className="text-[10px] text-[#9ca3af]">
          Real-time via SSE · /api/v1/agent-flow/stream
        </p>
      </div>
    </div>
  );
}
