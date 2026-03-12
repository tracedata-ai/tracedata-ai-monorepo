import SystemFlow from '@/components/system-flow/SystemFlow';

export default function SystemMapPage() {
  return (
    <div className="flex flex-col gap-6 p-8 h-[calc(100vh-2rem)]">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-100">System Intelligence Map</h1>
        <p className="text-zinc-400">
          Visualize the lifecycle of telemetry data as it flows through the TraceData multi-agent middleware.
        </p>
      </div>

      <div className="flex-1 w-full relative">
        <SystemFlow />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <h3 className="font-semibold text-zinc-200 mb-2">📡 Ingestion Layer</h3>
          <p className="text-zinc-500">
            Handles the 4-Ping lifecycle (Emergency, Normal, Start/End Trip). Deterministically routes telemetry and scrubs PII from driver inputs.
          </p>
        </div>
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <h3 className="font-semibold text-zinc-200 mb-2">🧠 Agentic Middleware</h3>
          <p className="text-zinc-500">
            LangGraph orchestrator manages 8 specialized sub-agents. Uses XGBoost for behavior and GenAI for sentiment and coaching.
          </p>
        </div>
        <div className="p-4 rounded-lg bg-zinc-900/50 border border-zinc-800">
          <h3 className="font-semibold text-zinc-200 mb-2">🛠️ Tooling (MCP)</h3>
          <p className="text-zinc-500">
            Model Context Protocol (MCP) enrichment provides real-time traffic and weather data to ensure fairness and accurate safety context.
          </p>
        </div>
      </div>
    </div>
  );
}
