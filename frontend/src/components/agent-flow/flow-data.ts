import type { Node, Edge } from "@xyflow/react";

export type AgentStatus = "idle" | "queued" | "running" | "success" | "warning" | "error";
export type WorkerHealthStatus = "healthy" | "degraded" | "unhealthy";

export interface AgentNodeData {
  label: string;
  subtitle: string;
  status: AgentStatus;
  elapsed?: string;
  workerHealth?: WorkerHealthStatus;
  type: "source" | "tool" | "agent" | "queue" | "output";
  [key: string]: unknown;
}

export const initialNodes: Node<AgentNodeData>[] = [
  // Row 0 — Source
  {
    id: "telemetry-ingestion",
    type: "agentNode",
    position: { x: 0, y: 160 },
    data: {
      label: "Telemetry Ingestion",
      subtitle: "IoT / GPS / CAN bus",
      status: "success",
      elapsed: "1s",
      type: "source",
    },
  },

  // Row 1 — Tool Gateway
  {
    id: "ingestion-validator",
    type: "agentNode",
    position: { x: 280, y: 60 },
    data: {
      label: "Ingestion Validator",
      subtitle: "Tool Gateway",
      status: "success",
      elapsed: "0.3s",
      type: "tool",
    },
  },
  {
    id: "context-enrichment",
    type: "agentNode",
    position: { x: 280, y: 260 },
    data: {
      label: "Context Enrichment",
      subtitle: "Tool Gateway",
      status: "running",
      elapsed: "1.2s",
      type: "tool",
    },
  },

  // Row 2 — Orchestrator
  {
    id: "orchestrator",
    type: "agentNode",
    position: { x: 580, y: 160 },
    data: {
      label: "Orchestrator Agent",
      subtitle: "Router + Audit Log",
      status: "running",
      elapsed: "2.1s",
      type: "agent",
    },
  },

  // Row 3 — Redis Queue
  {
    id: "redis-queue",
    type: "agentNode",
    position: { x: 880, y: 160 },
    data: {
      label: "Redis Priority Queue",
      subtitle: "critical / high / medium / low",
      status: "success",
      elapsed: "<5ms",
      type: "queue",
    },
  },

  // Row 4 — Specialist Agents
  {
    id: "scoring",
    type: "agentNode",
    position: { x: 1180, y: 0 },
    data: {
      label: "Scoring Agent",
      subtitle: "XGBoost + AIF360 + SHAP",
      status: "idle",
      elapsed: "—",
      type: "agent",
    },
  },
  {
    id: "safety",
    type: "agentNode",
    position: { x: 1180, y: 130 },
    data: {
      label: "Safety Agent",
      subtitle: "Emergency + Alert",
      status: "idle",
      elapsed: "—",
      type: "agent",
    },
  },
  {
    id: "sentiment",
    type: "agentNode",
    position: { x: 1180, y: 260 },
    data: {
      label: "Sentiment Agent",
      subtitle: "Burnout Detection",
      status: "running",
      elapsed: "1.8s",
      type: "agent",
    },
  },
  {
    id: "support",
    type: "agentNode",
    position: { x: 1180, y: 390 },
    data: {
      label: "Support Agent",
      subtitle: "Appeals + Coaching (RAG)",
      status: "idle",
      elapsed: "—",
      type: "agent",
    },
  },

  // Row 5 — Output
  {
    id: "output",
    type: "agentNode",
    position: { x: 1480, y: 160 },
    data: {
      label: "Fleet Manager / Driver",
      subtitle: "Notification + Dashboard",
      status: "success",
      elapsed: "4.8s",
      type: "output",
    },
  },
];

const edgeStyle = { stroke: "#d1d5db", strokeWidth: 1.5 };

export const initialEdges: Edge[] = [
  // Ingestion → Tool Gateways
  {
    id: "e-ing-val",
    source: "telemetry-ingestion",
    target: "ingestion-validator",
    animated: true,
    style: edgeStyle,
  },
  {
    id: "e-ing-ctx",
    source: "telemetry-ingestion",
    target: "context-enrichment",
    animated: true,
    style: edgeStyle,
  },

  // Tool Gateways → Orchestrator
  {
    id: "e-val-orch",
    source: "ingestion-validator",
    target: "orchestrator",
    animated: true,
    style: edgeStyle,
  },
  {
    id: "e-ctx-orch",
    source: "context-enrichment",
    target: "orchestrator",
    animated: true,
    style: edgeStyle,
  },

  // Orchestrator → Redis Queue
  {
    id: "e-orch-queue",
    source: "orchestrator",
    target: "redis-queue",
    animated: true,
    style: { ...edgeStyle, stroke: "#6366f1" },
  },

  // Queue → Agents
  {
    id: "e-queue-scoring",
    source: "redis-queue",
    target: "scoring",
    animated: false,
    style: edgeStyle,
  },
  {
    id: "e-queue-safety",
    source: "redis-queue",
    target: "safety",
    animated: true,
    style: { ...edgeStyle, stroke: "#fca5a5" },
  },
  {
    id: "e-queue-sentiment",
    source: "redis-queue",
    target: "sentiment",
    animated: true,
    style: edgeStyle,
  },
  {
    id: "e-queue-support",
    source: "redis-queue",
    target: "support",
    animated: false,
    style: edgeStyle,
  },

  // Agents → Output
  {
    id: "e-scoring-out",
    source: "scoring",
    target: "output",
    style: edgeStyle,
  },
  {
    id: "e-safety-out",
    source: "safety",
    target: "output",
    style: { ...edgeStyle, stroke: "#fca5a5" },
  },
  {
    id: "e-sentiment-out",
    source: "sentiment",
    target: "output",
    style: edgeStyle,
  },
  {
    id: "e-support-out",
    source: "support",
    target: "output",
    style: edgeStyle,
  },
];
