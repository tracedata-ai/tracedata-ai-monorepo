'use client';

import React, { memo } from 'react';
import { Handle, Position, NodeProps, Node } from '@xyflow/react';

export type KafkaNodeData = Node<{
  label: string;
  queueDepth: number;
  maxQueueDepth: number;
}>;

const KafkaNode = ({ data }: NodeProps<KafkaNodeData>) => {
  const { label, queueDepth, maxQueueDepth } = data;
  const percentage = Math.min((queueDepth / maxQueueDepth) * 100, 100);

  // Dynamic coloring logic
  const getColor = () => {
    if (queueDepth < 5) return 'bg-emerald-500';
    if (queueDepth < 15) return 'bg-amber-500';
    return 'bg-red-500';
  };

  const getBorderColor = () => {
    if (queueDepth < 5) return 'border-emerald-200';
    if (queueDepth < 15) return 'border-amber-200';
    return 'border-red-200';
  };

  return (
    <div className={`px-4 py-3 shadow-sm rounded-xl border-2 transition-all duration-500 ${getBorderColor()} bg-white min-w-[200px]`}>
      <Handle type="target" position={Position.Top} className="w-3 h-3 bg-zinc-200" />
      
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between">
          <span className="text-zinc-500 text-xs font-bold uppercase tracking-wider">{label}</span>
          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${getColor()} text-white font-bold`}>
            {queueDepth} MSG
          </span>
        </div>

        <div className="h-2 w-full bg-zinc-100 rounded-full overflow-hidden border border-zinc-200">
          <div 
            className={`h-full ${getColor()} transition-all duration-500 ease-out`}
            style={{ width: `${percentage}%` }}
          />
        </div>

        <div className="flex justify-between items-center text-[10px] text-zinc-400 font-medium">
          <span>Backpressure</span>
          <span>{percentage.toFixed(0)}%</span>
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3 bg-zinc-200" />
    </div>
  );
};

export default memo(KafkaNode);
