import { z } from "zod";

export const IssuePrioritySchema = z.enum(["Critical", "High", "Medium", "Low"]);

export const IssueStatusSchema = z.enum(["Open", "Overdue", "Resolved", "Closed"]);

export const IssueTimelineEventSchema = z.object({
  title: z.string(),
  timestamp: z.string(),
  description: z.string(),
});

export const IssueSchema = z.object({
  id: z.string(),
  vehicleId: z.string(),
  assetName: z.string(),
  priority: IssuePrioritySchema,
  type: z.string(),
  summary: z.string(),
  agent: z.string(),
  agentReasoning: z.string().optional(),
  agentTags: z.array(z.string()).optional(),
  status: IssueStatusSchema,
  reportedDate: z.string(),
  resolvedDate: z.string().optional(),
  technician: z.string().optional(),
  resolutionAction: z.string().optional(),
  timeline: z.array(IssueTimelineEventSchema),
  relatedDriverId: z.string().optional(),
  relatedTripId: z.string().optional(),
});

export type IssuePriority = z.infer<typeof IssuePrioritySchema>;
export type IssueStatus = z.infer<typeof IssueStatusSchema>;
export type IssueTimelineEvent = z.infer<typeof IssueTimelineEventSchema>;
export type Issue = z.infer<typeof IssueSchema>;
