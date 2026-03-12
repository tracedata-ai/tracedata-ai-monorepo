import { z } from "zod";

export const AgentStatusSchema = z.enum(["Active", "Idle", "Warning", "Error"]);

export const AgentTypeSchema = z.enum(["Governance", "Orchestration", "Analysis", "Action"]);

export const AgentLastActionSchema = z.object({
  message: z.string(),
  timestamp: z.string(),
});

export const AgentSchema = z.object({
  id: z.string(),
  name: z.string(),
  type: AgentTypeSchema,
  status: AgentStatusSchema,
  loadPercentage: z.number().min(0).max(100),
  description: z.string().optional(),
  lastAction: AgentLastActionSchema.optional(),
  uptime: z.string().optional(),
  confidenceScore: z.number().min(0).max(1).optional(),
  latencyMs: z.number().optional(),
});

export const OrchestrationSeveritySchema = z.enum(["info", "warning", "error"]);

export const OrchestrationEventSchema = z.object({
  id: z.string(),
  agentId: z.string(),
  agentName: z.string(),
  message: z.string(),
  timestamp: z.string(),
  severity: OrchestrationSeveritySchema,
  relatedEntityId: z.string().optional(),
  relatedEntityType: z.enum(["driver", "vehicle", "trip", "issue", "route"]).optional(),
});

export type Agent = z.infer<typeof AgentSchema>;
export type AgentStatus = z.infer<typeof AgentStatusSchema>;
export type AgentType = z.infer<typeof AgentTypeSchema>;
export type AgentLastAction = z.infer<typeof AgentLastActionSchema>;
export type OrchestrationEvent = z.infer<typeof OrchestrationEventSchema>;
export type OrchestrationSeverity = z.infer<typeof OrchestrationSeveritySchema>;
