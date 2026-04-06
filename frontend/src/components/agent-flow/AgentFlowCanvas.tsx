"use client";

import { useEffect, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type NodeTypes,
  type NodeMouseHandler,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { AgentNode } from "./AgentNode";
import {
  initialNodes,
  initialEdges,
  type AgentStatus,
  type AgentNodeData,
  type WorkerHealthStatus,
} from "./flow-data";
import { connectAgentFlowStream, type AgentFlowEvent, type AgentFlowSnapshot } from "@/lib/api";

const nodeTypes: NodeTypes = { agentNode: AgentNode as NodeTypes[string] };

interface AgentFlowCanvasProps {
  live: boolean;
  onConnectionChange?: (state: "connected" | "offline") => void;
  onNodeInspect?: (details: AgentNodeInspectDetails | null) => void;
}

const AGENT_NODE_MAP: Record<string, string> = {
  orchestrator: "orchestrator",
  scoring: "scoring",
  safety: "safety",
  sentiment: "sentiment",
  support: "support",
};

const NODE_AGENT_MAP: Record<string, string> = Object.fromEntries(
  Object.entries(AGENT_NODE_MAP).map(([agent, nodeId]) => [nodeId, agent])
);

export interface AgentNodeInspectDetails {
  nodeId: string;
  agent: string;
  label: string;
  status: AgentStatus;
  workerHealth?: WorkerHealthStatus;
  tripId?: string | null;
  events: AgentFlowEvent[];
}

export function AgentFlowCanvas({ live, onConnectionChange, onNodeInspect }: AgentFlowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);
  const lastSeqRef = useRef(0);
  const eventSourceRef = useRef<EventSource | null>(null);
  const eventHistoryRef = useRef<Record<string, AgentFlowEvent[]>>({});
  const selectedNodeIdRef = useRef<string | null>(null);

  const emitInspectForNode = (nodeId: string) => {
    const node = nodes.find((n) => n.id === nodeId);
    if (!node) return;
    const agent = NODE_AGENT_MAP[nodeId];
    if (!agent) return;
    const data = node.data as AgentNodeData;
    const events = eventHistoryRef.current[agent] || [];
    const latestTrip = events[0]?.trip_id;
    onNodeInspect?.({
      nodeId,
      agent,
      label: String(data.label),
      status: data.status as AgentStatus,
      workerHealth: data.workerHealth,
      tripId: latestTrip ?? null,
      events,
    });
  };

  const updateExecution = (agent: string, status: AgentStatus) => {
    const nodeId = AGENT_NODE_MAP[agent];
    if (!nodeId) return;
    setNodes((prev) =>
      prev.map((n) => {
        if (n.id !== nodeId) return n;
        const d = n.data as AgentNodeData;
        return { ...n, data: { ...d, status } };
      })
    );
  };

  const updateHealth = (agent: string, workerHealth: WorkerHealthStatus) => {
    const nodeId = AGENT_NODE_MAP[agent];
    if (!nodeId) return;
    setNodes((prev) =>
      prev.map((n) => {
        if (n.id !== nodeId) return n;
        const d = n.data as AgentNodeData;
        return { ...n, data: { ...d, workerHealth } };
      })
    );
  };

  const applySnapshot = (snapshot: AgentFlowSnapshot) => {
    const seq = snapshot.seq || 0;
    lastSeqRef.current = seq;
    Object.entries(snapshot.execution || {}).forEach(([agent, status]) => {
      updateExecution(agent, status as AgentStatus);
    });
    Object.entries(snapshot.worker_health || {}).forEach(([agent, status]) => {
      updateHealth(agent, status as WorkerHealthStatus);
    });
  };

  const applyEvent = (event: AgentFlowEvent) => {
    if (!event.seq || event.seq <= lastSeqRef.current) return;
    lastSeqRef.current = event.seq;
    const history = eventHistoryRef.current[event.agent] || [];
    eventHistoryRef.current[event.agent] = [event, ...history].slice(0, 25);
    if (event.event_type === "worker_health") {
      updateHealth(event.agent, event.status as WorkerHealthStatus);
      return;
    }
    updateExecution(event.agent, event.status as AgentStatus);
  };

  const onNodeClick: NodeMouseHandler = (_evt, node) => {
    selectedNodeIdRef.current = node.id;
    emitInspectForNode(node.id);
  };

  useEffect(() => {
    if (!live) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      onConnectionChange?.("offline");
      return;
    }

    const source = connectAgentFlowStream({
      onSnapshot: (snapshot) => {
        onConnectionChange?.("connected");
        applySnapshot(snapshot);
      },
      onEvent: (event) => {
        onConnectionChange?.("connected");
        applyEvent(event);
      },
      onError: () => onConnectionChange?.("offline"),
    });
    eventSourceRef.current = source;

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
    };
  }, [live, onConnectionChange]);

  useEffect(() => {
    if (selectedNodeIdRef.current) {
      emitInspectForNode(selectedNodeIdRef.current);
    }
  }, [nodes]);

  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-[#e5e7eb] bg-[#f9fafb] shadow-sm">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.18 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#e5e7eb"
        />
        <Controls className="!border-[#e5e7eb] !bg-white !shadow-sm [&>button]:!border-[#e5e7eb] [&>button]:!bg-white [&>button]:!fill-[#6b7280] [&>button:hover]:!bg-[#f3f4f6]" />
      </ReactFlow>
    </div>
  );
}
