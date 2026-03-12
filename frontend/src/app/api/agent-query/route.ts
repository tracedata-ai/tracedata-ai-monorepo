/**
 * API route: Query Orchestrator Agent.
 * RUBRIC: Clean Architecture—agent boundary (A1).
 * Reference: Agent Topology, section 2.2.1
 */

import {
  isValidJWT,
  sanitizeTenantId,
  secureHeaders,
} from "@/lib/utils/security";
import type { OrchestratorResponse } from "@/lib/types/agents";

interface OrchestratorQueryRequest {
  question: string;
  context?: Record<string, unknown>;
}

export async function POST(request: Request) {
  try {
    // Validate tenant context
    const tenantId = request.headers.get("x-tenant-id");
    if (!tenantId) {
      return new Response(
        JSON.stringify({ error: "Tenant context required" }),
        { status: 403, headers: { "Content-Type": "application/json" } },
      );
    }

    const sanitized = sanitizeTenantId(tenantId);
    if (sanitized !== tenantId) {
      return new Response(
        JSON.stringify({ error: "Invalid tenant ID format" }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    // Validate JWT
    const authHeader = request.headers.get("authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return new Response(
        JSON.stringify({ error: "Missing or invalid authorization header" }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      );
    }

    const token = authHeader.slice(7);
    if (!isValidJWT(token)) {
      return new Response(JSON.stringify({ error: "Invalid JWT token" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Parse request body
    let body: OrchestratorQueryRequest;
    try {
      body = await request.json();
    } catch {
      return new Response(
        JSON.stringify({ error: "Invalid JSON in request body" }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    const { question, context } = body;

    // Validate question
    if (!question || typeof question !== "string" || question.length > 1000) {
      return new Response(
        JSON.stringify({
          error: "Invalid or missing question (max 1000 chars)",
        }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    // POC: Return mock Orchestrator response
    // In production, this would forward to FastAPI + LangGraph backend
    const mockResponse: OrchestratorResponse = {
      result: `Query from tenant ${tenantId}: "${question}" has been processed.`,
      reasoning:
        "Mock orchestrator response for POC. In production, routes to LangGraph workflow.",
      confidence: 0.95,
      agentsInvolved: ["orchestrator", "context_enrichment"],
    };

    return new Response(JSON.stringify(mockResponse), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        ...secureHeaders,
      },
    });
  } catch (error) {
    console.error("POST /api/agent-query error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
