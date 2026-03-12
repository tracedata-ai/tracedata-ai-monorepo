'use client';

import React, { useCallback } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  BackgroundVariant,
  Position,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';

import { initialNodes, initialEdges } from './flow-data';
import KafkaNode from './KafkaNode';
import dagre from 'dagre';

const nodeTypes = {
  kafka: KafkaNode,
};

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 200;
const nodeHeight = 80;

const getLayoutedElements = (nodes: any[], edges: any[], direction = 'TB') => {
  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction });

  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  const newNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    return {
      ...node,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      position: {
        x: nodeWithPosition.x - nodeWidth / 2,
        y: nodeWithPosition.y - nodeHeight / 2,
      },
    };
  });

  return { nodes: newNodes, edges };
};

const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
  initialNodes,
  initialEdges
);

export default function SystemFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  // Simulation logic for Kafka Queue Depth
  React.useEffect(() => {
    const interval = setInterval(() => {
      setNodes((nds) =>
        nds.map((node) => {
          if (node.type === 'kafka') {
            const currentDepth = (node.data as any).queueDepth || 0;
            // Randomly fluctuate between 0 and 20
            const change = Math.floor(Math.random() * 5) - 2;
            const newDepth = Math.max(0, Math.min(20, currentDepth + change));
            
            return {
              ...node,
              data: {
                ...node.data,
                queueDepth: newDepth,
              },
            };
          }
          return node;
        })
      );
    }, 2000);

    return () => clearInterval(interval);
  }, [setNodes]);

  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge(params, eds)),
    [setEdges],
  );

  return (
    <div className="w-full h-full min-h-[800px] border border-zinc-200 rounded-xl overflow-hidden bg-white shadow-sm transition-all duration-300">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        nodesDraggable={false}
        className="text-zinc-600"
        colorMode="light"
      >
        <Controls className="bg-white border-zinc-200 fill-zinc-600 shadow-sm" />
        <MiniMap 
          className="bg-zinc-50 border border-zinc-200 rounded-lg overflow-hidden shadow-sm" 
          nodeColor={(n) => {
            if (n.className?.includes('border-red-')) return '#fee2e2';
            if (n.className?.includes('border-blue-')) return '#dbeafe';
            if (n.className?.includes('border-amber-')) return '#fef3c7';
            if (n.className?.includes('border-purple-')) return '#f3e8ff';
            return '#f4f4f5';
          }}
        />
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#e4e4e7" />
      </ReactFlow>
    </div>
  );
}
