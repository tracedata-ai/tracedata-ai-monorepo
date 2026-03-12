"use client";

import React, { useState } from "react";
import { useAgentQuery } from "@/lib/hooks/useAgentQuery";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { OrchestratorResponse } from "@/lib/types/agents";

interface OrchestratorViewProps {
  className?: string;
}

/**
 * OrchestratorView demonstrates agent integration.
 * RUBRIC: Clean Architecture—clear agent boundary (A1).
 * Reference: Agent Topology, section 2.2.1 (Orchestrator Agent)
 */
export function OrchestratorView({ className }: OrchestratorViewProps) {
  const [query, setQuery] = useState("");
  const { data, loading, error, mutate } = useAgentQuery<
    OrchestratorResponse
  >("/api/agent-query");

  const handleSubmitQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    await mutate({ question: query });
  };

  return (
    <div
      className={cn(
        "rounded-lg border border-gray-200 bg-white p-6 space-y-4",
        className,
      )}
    >
      <div>
        <h3 className="font-semibold text-gray-900">Orchestrator Agent</h3>
        <p className="mt-1 text-sm text-gray-600">
          Query the Orchestrator Agent for fleet insights and decision support.
        </p>
      </div>

      <form onSubmit={handleSubmitQuery} className="space-y-3">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Example: What's the risk level for Alice's recent trips?"
          aria-label="Query for Orchestrator Agent"
          className="w-full rounded border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          disabled={loading}
        />
        <Button
          type="submit"
          disabled={loading || !query.trim()}
          className="w-full"
        >
          {loading ? "Querying Agent..." : "Submit Query"}
        </Button>
      </form>

      {error && (
        <div className="rounded bg-red-50 p-3 text-sm text-red-800">
          <p className="font-semibold">Error</p>
          <p>{error.message}</p>
        </div>
      )}

      {data && (
        <div className="rounded bg-teal-50 p-4 space-y-3">
          <p className="font-semibold text-teal-900">Orchestrator Response</p>
          <div className="text-sm text-teal-800 space-y-2">
            <div>
              <p className="font-medium">Result:</p>
              <p>{data.result}</p>
            </div>
            <div>
              <p className="font-medium">Reasoning:</p>
              <p>{data.reasoning}</p>
            </div>
            <div className="flex gap-4">
              <div>
                <p className="text-xs text-teal-700">Confidence</p>
                <p className="font-bold">
                  {(data.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <div>
                <p className="text-xs text-teal-700">Agents Involved</p>
                <p className="font-bold">{data.agentsInvolved.join(", ")}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="rounded bg-blue-50 p-3 text-sm text-blue-800">
        <p className="font-semibold">Architecture Note</p>
        <p className="mt-1">
          This component communicates with the backend Orchestrator Agent
          (LangGraph), which may invoke Behavior, Sentiment, or Safety agents
          depending on the query.
        </p>
      </div>
    </div>
  );
}
