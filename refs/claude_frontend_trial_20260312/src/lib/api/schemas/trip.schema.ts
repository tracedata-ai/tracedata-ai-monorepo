import { z } from "zod";
import { XaiExplanationSchema } from "./driver.schema";

export const TripStatusSchema = z.enum(["In Progress", "Completed", "Scheduled", "Cancelled"]);

export const TelemetrySegmentSchema = z.object({
  timestamp: z.string(),
  speed: z.number().nonnegative(),
  brakePressure: z.number().min(0).max(100),
  throttlePos: z.number().min(0).max(100),
  isSafeZone: z.boolean(),
  rewardType: z.string().optional(),
});

export const TripSchema = z.object({
  id: z.string(),
  vehicleId: z.string(),
  driverId: z.string(),
  routeId: z.string(),
  status: TripStatusSchema,
  startTime: z.string(), // ISO
  historicalAvgMins: z.number().positive(),
  actualDurationMins: z.number().nonnegative().optional(),
  distanceKm: z.number().positive(),
  currentDistanceKm: z.number().nonnegative().optional(),
  score: z.number().min(0).max(100).optional(),
  explanation: XaiExplanationSchema.optional(),
  telemetrySegments: z.array(TelemetrySegmentSchema).optional(),
  nationalSpeedLimit: z.number().optional(),
  relatedIssueId: z.string().optional(),
  agentEventId: z.string().optional(),
});

export type TripStatus = z.infer<typeof TripStatusSchema>;
export type TelemetrySegment = z.infer<typeof TelemetrySegmentSchema>;
export type Trip = z.infer<typeof TripSchema>;
