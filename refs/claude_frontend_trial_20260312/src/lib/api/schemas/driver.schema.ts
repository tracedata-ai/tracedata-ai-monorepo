import { z } from "zod";

export const XaiExplanationSchema = z.object({
  humanSummary: z.string(),
  featureImportance: z.record(z.string(), z.number()),
  fairnessAuditScore: z.number(),
});

export const TripHistoryEntrySchema = z.object({
  tripId: z.string(),
  score: z.number().min(0).max(100),
  date: z.string(), // ISO
});

export const DriverStatusSchema = z.enum(["Active", "On Break", "Off Duty"]);

export const LicenseStatusSchema = z.enum(["Valid", "Expiring Soon", "Expired"]);

export const DriverSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: DriverStatusSchema,
  tripsCompleted: z.number().int().nonnegative(),
  rating: z.number().min(1).max(5),
  avgTripScore: z.number().min(0).max(100),
  licenseStatus: LicenseStatusSchema,
  recentIncidents: z.number().int().nonnegative(),
  explanation: XaiExplanationSchema.optional(),
  tripHistory: z.array(TripHistoryEntrySchema),
});

export type XaiExplanation = z.infer<typeof XaiExplanationSchema>;
export type TripHistoryEntry = z.infer<typeof TripHistoryEntrySchema>;
export type Driver = z.infer<typeof DriverSchema>;
export type DriverStatus = z.infer<typeof DriverStatusSchema>;
export type LicenseStatus = z.infer<typeof LicenseStatusSchema>;
