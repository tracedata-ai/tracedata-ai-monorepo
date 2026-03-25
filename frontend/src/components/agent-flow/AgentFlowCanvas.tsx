"use client";

import { useCallback, useEffect, useRef } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  type NodeTypes,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { AgentNode } from "./AgentNode";
import {
  initialNodes,
  initialEdges,
  type AgentStatus,
  type AgentNodeData,
} from "./flow-data";

const nodeTypes: NodeTypes = { agentNode: AgentNode as NodeTypes[string] };

const STATUS_CYCLE: AgentStatus[] = ["idle", "running", "success"];

interface AgentFlowCanvasProps {
  simulating: boolean;
}

export function AgentFlowCanvas({ simulating }: AgentFlowCanvasProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const runStep = useCallback(() => {
    setNodes((prev) => {
      const agentIds = prev
        .filter((n) => (n.data as AgentNodeData).type === "agent")
        .map((n) => n.id);
      const targetId = agentIds[Math.floor(Math.random() * agentIds.length)];
      return prev.map((n) => {
        if (n.id !== targetId) return n;
        const d = n.data as AgentNodeData;
        const currentIdx = STATUS_CYCLE.indexOf(d.status as AgentStatus);
        const next = STATUS_CYCLE[(currentIdx + 1) % STATUS_CYCLE.length];
        const elapsedMap: Record<AgentStatus, string> = {
          idle: "—",
          running: `${(Math.random() * 2 + 0.5).toFixed(1)}s`,
          success: `${(Math.random() * 3 + 1).toFixed(1)}s`,
          warning: "—",
          error: "—",
        };
        return {
          ...n,
          data: { ...d, status: next, elapsed: elapsedMap[next] },
        };
      });
    });
  }, [setNodes]);

  useEffect(() => {
    if (simulating) {
      intervalRef.current = setInterval(runStep, 2000);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [simulating, runStep]);

  return (
    <div className="h-full w-full rounded-xl overflow-hidden border border-[#e5e7eb] bg-[#f9fafb] shadow-sm">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
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
