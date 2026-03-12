import { Node, Edge } from '@xyflow/react';

export const initialNodes: Node[] = [
  // External Streams
  {
    id: 'trucks',
    type: 'input',
    data: { label: '🚚 10K+ Trucks' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-800 border-blue-200 rounded-xl p-4 font-bold shadow-sm',
  },
  {
    id: 'kafka',
    type: 'kafka',
    data: { label: 'Kafka Queue', queueDepth: 0, maxQueueDepth: 20 },
    position: { x: 0, y: 0 },
    draggable: false,
  },

  // Ingestion Layer
  {
    id: 'ingestion-agent',
    data: { label: 'Quality Ingestion Agent\n(Deterministic Router)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-700 border-indigo-200 rounded-xl p-4 font-semibold shadow-sm',
  },
  {
    id: 'pii-scrubber',
    data: { label: 'PII Scrubber Agent\n(GenAI/NLP)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-600 border-purple-200 rounded-xl p-4 shadow-sm',
  },

  // Persistence
  {
    id: 'db',
    data: { label: '🗄️ PostgreSQL\n(Flat Schema)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-700 border-zinc-200 rounded-xl p-4 shadow-sm font-medium',
  },

  // Orchestration
  {
    id: 'orchestrator',
    data: { label: '🧠 LangGraph Orchestrator\n(State Machine)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-800 border-amber-200 rounded-xl p-6 font-bold shadow-md border-2',
  },

  // Specialized Agents
  {
    id: 'behavior-agent',
    data: { label: 'Behavior Agent\n(XGBoost / AIF360)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-zinc-600 border-slate-200 rounded-xl p-4 shadow-sm',
  },
  {
    id: 'safety-agent',
    data: { label: 'Safety Agent\n(Cyclical Loop)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-red-600 border-red-200 rounded-xl p-4 shadow-sm font-semibold',
  },
  {
    id: 'sentiment-agent',
    data: { label: 'Sentiment Agent\n(Burnout Risk)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-pink-600 border-pink-200 rounded-xl p-4 shadow-sm',
  },
  {
    id: 'coaching-agent',
    data: { label: 'Coaching Agent\n(GenAI)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-cyan-600 border-cyan-200 rounded-xl p-4 shadow-sm',
  },
  {
    id: 'advocacy-agent',
    data: { label: 'Advocacy Agent\n(Appeals Logic)' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-emerald-600 border-emerald-200 rounded-xl p-4 shadow-sm',
  },

  // Tools
  {
    id: 'mcp-tool',
    data: { label: 'MCP Tool\nContext Enrichment' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-white text-violet-600 border-violet-200 border-dashed rounded-xl p-4 shadow-sm',
  },

  // Frontend
  {
    id: 'frontend',
    type: 'output',
    data: { label: '🖥️ Next.js Dashboard' },
    position: { x: 0, y: 0 },
    draggable: false,
    className: 'bg-zinc-800 text-white border-zinc-900 rounded-xl p-4 font-bold shadow-lg',
  },
];

export const initialEdges: Edge[] = [
  { id: 'e-t-k', source: 'trucks', target: 'kafka', label: 'Telemetry stream', animated: true, type: 'step', style: { strokeDasharray: '5,5', stroke: '#94a3b8' } },
  { id: 'e-k-i', source: 'kafka', target: 'ingestion-agent', label: '4-ping ingest', animated: true, type: 'step', style: { strokeDasharray: '5,5', stroke: '#94a3b8' } },
  { id: 'e-i-p', source: 'ingestion-agent', target: 'pii-scrubber', label: 'Driver text', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'e-p-d', source: 'pii-scrubber', target: 'db', label: 'Sanitized', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'e-i-d', source: 'ingestion-agent', target: 'db', label: 'Cleaned telemetry', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'e-d-o', source: 'db', target: 'orchestrator', label: 'Event trigger', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  
  // Orchestrator to Specialized Agents
  { id: 'o-behavior', source: 'orchestrator', target: 'behavior-agent', label: 'End of Trip', animated: true, style: { strokeDasharray: '5,5', stroke: '#94a3b8' } },
  { id: 'o-safety', source: 'orchestrator', target: 'safety-agent', label: 'Emergency Ping', animated: true, style: { strokeDasharray: '5,5', stroke: '#ef4444' } },
  { id: 'o-sentiment', source: 'orchestrator', target: 'sentiment-agent', label: 'Feedback/Appeals', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'o-coaching', source: 'orchestrator', target: 'coaching-agent', label: 'Personalize', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'o-advocacy', source: 'orchestrator', target: 'advocacy-agent', label: 'Formulate Case', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },

  // Specialized Agents back to O/DB or Context
  { id: 'tools-context', source: 'behavior-agent', target: 'mcp-tool', label: 'Traffic/Weather', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  { id: 'safety-context', source: 'safety-agent', target: 'mcp-tool', label: 'Contextual alert', style: { strokeDasharray: '5,5', stroke: '#cbd5e1' } },
  
  // Frontend
  { id: 'o-frontend', source: 'orchestrator', target: 'frontend', label: 'Real-time state updates', animated: true, style: { strokeDasharray: '5,5', stroke: '#94a3b8' } },
];
