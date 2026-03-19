"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import type { AgentNodeData, AgentStatus } from "./flow-data";

// ── Status config ──────────────────────────────────────────────────────
const statusConfig: Record<
  AgentStatus,
  { ring: string; label: string; icon: string; bg: string }
> = {
  idle:    { ring: "ring-[#d1d5db]/60", label: "text-[#6b7280]", icon: "○", bg: "bg-[#f3f4f6]" },
  running: { ring: "ring-[#f59e0b]/40", label: "text-[#d97706]", icon: "◌", bg: "bg-[#fef3c7]" },
  success: { ring: "ring-[#22c55e]/40", label: "text-[#16a34a]", icon: "✓", bg: "bg-[#dcfce7]" },
  warning: { ring: "ring-[#fb923c]/40", label: "text-[#ea580c]", icon: "⚠", bg: "bg-[#ffedd5]" },
  error:   { ring: "ring-[#ef4444]/40", label: "text-[#dc2626]", icon: "✕", bg: "bg-[#fee2e2]" },
};

const typeAccent: Record<AgentNodeData["type"], string> = {
  source: "border-l-[#3b82f6]",
  tool:   "border-l-[#8b5cf6]",
  agent:  "border-l-[#6366f1]",
  queue:  "border-l-[#f59e0b]",
  output: "border-l-[#22c55e]",
};

function RunningSpinner() {
  return (
    <svg className="animate-spin" width="10" height="10" viewBox="0 0 10 10" fill="none">
      <circle cx="5" cy="5" r="4" stroke="#f59e0b" strokeWidth="1.5" strokeOpacity="0.3" />
      <path d="M5 1 A4 4 0 0 1 9 5" stroke="#d97706" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function AgentNodeComponent(props: NodeProps) {
  const data = props.data as AgentNodeData;
  const cfg = statusConfig[data.status as AgentStatus] ?? statusConfig.idle;
  const accent = typeAccent[data.type as AgentNodeData["type"]] ?? "border-l-[#d1d5db]";

  return (
    <div
      className={`
        group relative min-w-[180px] max-w-[210px] rounded-lg
        border border-[#e5e7eb] border-l-4 ${accent}
        bg-white shadow-sm shadow-black/8
        transition-all duration-200
        hover:border-[#d1d5db] hover:shadow-md
      `}
    >
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !border-[#d1d5db] !bg-white"
      />

      <div className="p-3">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <div className={`flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full ring-2 ${cfg.ring} ${cfg.bg}`}>
            {data.status === "running" ? (
              <RunningSpinner />
            ) : (
              <span className={`text-[8px] font-bold leading-none ${cfg.label}`}>
                {cfg.icon}
              </span>
            )}
          </div>
          <span className="truncate text-[11px] font-semibold leading-tight text-[#111827]">
            {String(data.label)}
          </span>
        </div>

        {/* Subtitle */}
        <p className="ml-7 text-[9px] leading-relaxed text-[#9ca3af] truncate">
          {String(data.subtitle)}
        </p>

        {/* Footer */}
        <div className="ml-7 mt-2 flex items-center justify-between">
          <span className={`text-[9px] font-semibold uppercase tracking-wide ${cfg.label}`}>
            {String(data.status)}
          </span>
          {data.elapsed && (
            <span className="text-[9px] text-[#9ca3af]">{String(data.elapsed)}</span>
          )}
        </div>
      </div>

      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !border-[#d1d5db] !bg-white"
      />
    </div>
  );
}

export const AgentNode = memo(AgentNodeComponent);
