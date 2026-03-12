"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  BackgroundVariant,
  Handle,
  Position,
  type NodeProps,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

// ─── Types ───────────────────────────────────────────────────────────────────

type AgentStatus = "Active" | "Idle" | "Warning" | "Error";
type AgentTier   = "Governance" | "Orchestration" | "Analysis" | "Action";

interface AgentNodeData extends Record<string, unknown> {
  id: string;
  name: string;
  type: AgentTier;
  status: AgentStatus;
  loadPercentage?: number;
  highlighted?: boolean;
  onSelect?: (id: string) => void;
}

// ─── Colours ─────────────────────────────────────────────────────────────────

const TIER_COLOR: Record<AgentTier, string> = {
  Governance:    "#64748b",
  Orchestration: "#2575fc",
  Analysis:      "#a855f7",
  Action:        "#0d9488",
};

const STATUS_COLOR: Record<AgentStatus, string> = {
  Active:  "#0d9488",
  Idle:    "#64748b",
  Warning: "#f59e0b",
  Error:   "#ef4444",
};

// ─── Custom Agent Node ────────────────────────────────────────────────────────

function AgentNode({ data }: NodeProps) {
  const d = data as AgentNodeData;
  const tierColor   = TIER_COLOR[d.type]   ?? "#64748b";
  const statusColor = STATUS_COLOR[d.status] ?? "#64748b";
  const isIdle      = d.status === "Idle";

  return (
    <div
      onClick={() => d.onSelect?.(d.id)}
      className="cursor-pointer select-none"
      style={{
        width: 158,
        background: d.highlighted
          ? `linear-gradient(135deg, #0f172a 0%, ${tierColor}18 100%)`
          : "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        border: `1.5px solid ${d.highlighted ? tierColor : tierColor + "44"}`,
        borderRadius: 10,
        padding: "10px 12px",
        opacity: isIdle ? 0.5 : 1,
        boxShadow: d.highlighted
          ? `0 0 0 2px ${tierColor}33, 0 4px 16px ${tierColor}22`
          : "0 2px 8px rgba(0,0,0,0.4)",
        transition: "all 0.15s ease",
      }}
    >
      {/* Handles */}
      <Handle type="target" position={Position.Left}
        style={{ background: tierColor, width: 7, height: 7, border: "none", opacity: 0.8 }} />
      <Handle type="source" position={Position.Right}
        style={{ background: tierColor, width: 7, height: 7, border: "none", opacity: 0.8 }} />

      {/* Header row: ID + status dot */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 5 }}>
        <span style={{
          fontFamily: "ui-monospace, monospace",
          fontSize: 9,
          fontWeight: 700,
          color: tierColor,
          letterSpacing: "0.06em",
        }}>
          {d.id}
        </span>
        <span style={{
          width: 7, height: 7, borderRadius: "50%",
          background: statusColor,
          boxShadow: d.status === "Active" ? `0 0 5px ${statusColor}` : "none",
          flexShrink: 0,
        }} />
      </div>

      {/* Agent name */}
      <div style={{
        fontSize: 11.5,
        fontWeight: 700,
        color: "#f1f5f9",
        lineHeight: 1.25,
        marginBottom: 7,
      }}>
        {d.name}
      </div>

      {/* Type badge + load bar */}
      <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
        <span style={{
          display: "inline-block",
          fontSize: 8,
          fontWeight: 700,
          textTransform: "uppercase",
          letterSpacing: "0.07em",
          color: tierColor,
          background: tierColor + "18",
          border: `1px solid ${tierColor}33`,
          borderRadius: 4,
          padding: "1px 5px",
          alignSelf: "flex-start",
        }}>
          {d.type}
        </span>

        {d.loadPercentage !== undefined && (
          <div>
            <div style={{
              display: "flex", justifyContent: "space-between",
              fontSize: 8, color: "#64748b", marginBottom: 2,
            }}>
              <span>LOAD</span>
              <span style={{ color: "#94a3b8", fontFamily: "monospace" }}>{d.loadPercentage}%</span>
            </div>
            <div style={{ height: 2, background: "#1e293b", borderRadius: 2, overflow: "hidden" }}>
              <div style={{
                height: "100%", borderRadius: 2,
                width: `${d.loadPercentage}%`,
                background: d.status === "Warning" ? "#f59e0b" : d.status === "Idle" ? "#334155" : tierColor,
              }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

const nodeTypes = { agent: AgentNode };

// ─── Node + Edge definitions ──────────────────────────────────────────────────

const BASE_NODES: Array<Omit<Node, "data"> & { data: Omit<AgentNodeData, "highlighted" | "onSelect"> }> = [
  // Governance
  { id: "AG-01", type: "agent", position: { x: 0,   y: 80  }, data: { id: "AG-01", name: "Ingestion Quality", type: "Governance",    status: "Active",  loadPercentage: 62 } },
  { id: "AG-02", type: "agent", position: { x: 0,   y: 230 }, data: { id: "AG-02", name: "PII Scrubber",       type: "Governance",    status: "Active",  loadPercentage: 45 } },
  // Orchestration
  { id: "AG-03", type: "agent", position: { x: 230, y: 155 }, data: { id: "AG-03", name: "Orchestrator",        type: "Orchestration", status: "Active",  loadPercentage: 78 } },
  // Analysis
  { id: "AG-04", type: "agent", position: { x: 460, y: 40  }, data: { id: "AG-04", name: "Behavior",            type: "Analysis",      status: "Active",  loadPercentage: 55 } },
  { id: "AG-05", type: "agent", position: { x: 460, y: 175 }, data: { id: "AG-05", name: "Sentiment",           type: "Analysis",      status: "Idle",    loadPercentage: 10 } },
  { id: "AG-06", type: "agent", position: { x: 460, y: 310 }, data: { id: "AG-06", name: "Context",             type: "Analysis",      status: "Active",  loadPercentage: 41 } },
  // Action
  { id: "AG-07", type: "agent", position: { x: 690, y: 40  }, data: { id: "AG-07", name: "Safety",              type: "Action",        status: "Warning", loadPercentage: 88 } },
  { id: "AG-08", type: "agent", position: { x: 690, y: 185 }, data: { id: "AG-08", name: "Advocacy",            type: "Action",        status: "Active",  loadPercentage: 33 } },
  { id: "AG-09", type: "agent", position: { x: 690, y: 330 }, data: { id: "AG-09", name: "Coaching",            type: "Action",        status: "Active",  loadPercentage: 57 } },
];

const EDGES: Edge[] = [
  { id: "e01-03", source: "AG-01", target: "AG-03", animated: true },
  { id: "e02-03", source: "AG-02", target: "AG-03", animated: true },
  { id: "e03-04", source: "AG-03", target: "AG-04", animated: true },
  { id: "e03-05", source: "AG-03", target: "AG-05" },
  { id: "e03-06", source: "AG-03", target: "AG-06", animated: true },
  { id: "e04-07", source: "AG-04", target: "AG-07", animated: true },
  { id: "e04-08", source: "AG-04", target: "AG-08", animated: true },
  { id: "e04-09", source: "AG-04", target: "AG-09", animated: true },
  { id: "e05-09", source: "AG-05", target: "AG-09" },
  { id: "e06-07", source: "AG-06", target: "AG-07", animated: true },
].map((e) => ({
  ...e,
  type: "smoothstep",
  style: { stroke: "#334155", strokeWidth: 1.5 },
  markerEnd: { type: "arrowclosed" as const, color: "#475569", width: 14, height: 14 },
}));

// ─── Component ────────────────────────────────────────────────────────────────

interface AgentFlowDiagramProps {
  interactive?: boolean;
  onNodeClick?: (agentId: string) => void;
  highlightedId?: string;
}

export function AgentFlowDiagram({ interactive = false, onNodeClick, highlightedId }: AgentFlowDiagramProps) {
  const nodes: Node[] = BASE_NODES.map((n) => ({
    ...n,
    data: {
      ...n.data,
      highlighted: highlightedId === n.id,
      onSelect: interactive ? onNodeClick : undefined,
    },
    draggable: false,
    selectable: interactive,
  }));

  const onNodeClickHandler = useCallback(
    (_: React.MouseEvent, node: Node) => {
      if (interactive) onNodeClick?.(node.id);
    },
    [interactive, onNodeClick],
  );

  return (
    <div style={{ width: "100%", height: 420, borderRadius: 12, overflow: "hidden" }}>
      <ReactFlow
        nodes={nodes}
        edges={EDGES}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClickHandler}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.5}
        maxZoom={1.5}
        panOnDrag={false}
        zoomOnScroll={false}
        zoomOnDoubleClick={false}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={interactive}
        proOptions={{ hideAttribution: true }}
        style={{ background: "transparent" }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#1e293b"
        />
      </ReactFlow>
    </div>
  );
}
