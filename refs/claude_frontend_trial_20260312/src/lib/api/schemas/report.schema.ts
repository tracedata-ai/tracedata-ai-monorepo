import { z } from "zod";

export const ReportTypeSchema = z.enum(["PDF", "CSV", "JSON"]);

export const ReportSchema = z.object({
  id: z.string(),
  name: z.string(),
  date: z.string(),
  size: z.string(),
  type: ReportTypeSchema,
  agentTag: z.string(),
  confidenceScore: z.number().min(0).max(1),
  aiSummary: z.string(),
});

export type Report = z.infer<typeof ReportSchema>;
export type ReportType = z.infer<typeof ReportTypeSchema>;
