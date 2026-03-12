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
  Node,
} from '@xyflow/react';

import '@xyflow/react/dist/style.css';

import { initialNodes, initialEdges } from './flow-data';
import KafkaNode from './KafkaNode';
import dagre from 'dagre';

/**
 * Node Data Interface
 * Standardizes the data properties for all flow nodes.
 */
interface SystemNodeData extends Record<string, unknown> {
  label: string;
  status: 'idle' | 'processing' | 'alert' | 'error';
  queueDepth?: number;
}

type SystemNode = Node<SystemNodeData>;

const nodeTypes = {
  kafka: KafkaNode,
};

const dagreGraph = new dagre.graphlib.Graph();
dagreGraph.setDefaultEdgeLabel(() => ({}));

const nodeWidth = 200;
const nodeHeight = 80;

const getLayoutedElements = (nodes: SystemNode[], edges: Edge[], direction = 'TB') => {
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
  initialNodes as SystemNode[],
  initialEdges
);

export default function SystemFlow() {
  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  // Simulation logic for Kafka Queue Depth and Node Status Transitions
  React.useEffect(() => {
    const interval = setInterval(() => {
      // 1. Update Nodes
      setNodes((nds) => {
        const nextNodes = nds.map((node) => {
          // Kafka logic
          if (node.type === 'kafka') {
            const currentDepth = node.data.queueDepth || 0;
            const change = Math.floor(Math.random() * 5) - 2;
            const newDepth = Math.max(0, Math.min(20, currentDepth + change));
            
            let newStatus: 'idle' | 'processing' | 'alert' | 'error' = 'idle';
            if (newDepth > 15) newStatus = 'error';
            else if (newDepth > 8) newStatus = 'alert';
            else if (newDepth > 0) newStatus = 'processing';

            return {
              ...node,
              data: { ...node.data, queueDepth: newDepth, status: newStatus },
            };
          }

          if (node.id !== 'trucks' && node.id !== 'frontend') {
            if (Math.random() > 0.8) {
              const statuses: ('idle' | 'processing' | 'alert' | 'error')[] = ['idle', 'processing', 'alert'];
              const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];
              
              return {
                ...node,
                data: { ...node.data, status: randomStatus },
                className: `${node.className?.split(' border-')[0]} border-${
                  randomStatus === 'processing' ? 'blue-500' :
                  randomStatus === 'alert' ? 'orange-500' :
                  randomStatus === 'error' ? 'red-500' : 'zinc-200'
                } border-2`,
              };
            }
          }
          return node;
        });

        // 2. Update Edges immediately based on the new nodes
        setEdges((eds) => {
          return eds.map((edge) => {
            const sourceNode = nextNodes.find((n) => n.id === edge.source);
            if (!sourceNode) return edge;

            const status = sourceNode.data.status;
            let color = '#cbd5e1'; 
            let animated = false;

            if (status === 'processing') {
              color = '#3b82f6';
              animated = true;
            } else if (status === 'alert') {
              color = '#f97316';
              animated = true;
            } else if (status === 'error') {
              color = '#ef4444';
              animated = true;
            }

            return {
              ...edge,
              animated,
              style: { ...edge.style, stroke: color, strokeWidth: animated ? 2 : 1 },
            };
          });
        });

        return nextNodes;
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [setNodes, setEdges]);

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
