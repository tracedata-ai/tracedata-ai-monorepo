/**
 * Agent type definitions for TraceData.
 * RUBRIC: Clean Architecture—clear boundaries between agent interactions.
 * Reference: A1 (Agent Topology), A16 (Kafka integration)
 */

export interface OrchestratorRequest {
  question: string;
  context?: Record<string, unknown>;
}

export interface OrchestratorResponse {
  result: string;
  reasoning: string;
  confidence: number;
  agentsInvolved: string[];
}

export interface SafetyAgentAlert {
  eventId: string;
  driverId: string;
  tripId: string;
  severity: "warning" | "critical";
  interventionLevel: 1 | 2 | 3;
  message: string;
  timestamp: ISO8601String;
  tenantId: string;
  context: Record<string, unknown>;
}

export interface FeedbackAgentRequest {
  appeal: string;
  driverId: string;
  tripId: string;
  previousScores: number[];
}

export interface FeedbackAgentResponse {
  draftResponse: string;
  requiresHumanReview: boolean;
  escalationReason?: string;
  sentimentAnalysis: {
    score: 0 | 1; // 0=negative, 1=positive
    confidence: number;
  };
}

export interface ContextEnrichmentInput {
  lat: number;
  lon: number;
  timestamp: ISO8601String;
}

export interface ContextEnrichmentOutput {
  placeName: string;
  roadType: string;
  speedLimit: number;
  weather: {
    condition: string;
    temperature: number;
    windSpeed: number;
  };
  trafficCongestion: "light" | "moderate" | "heavy";
}

export type ISO8601String = string;
