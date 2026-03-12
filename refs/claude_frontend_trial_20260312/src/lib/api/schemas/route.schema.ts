import { z } from "zod";

export const RouteStatusSchema = z.enum(["Active", "Inactive"]);

export const RouteSchema = z.object({
  id: z.string(),
  name: z.string(),
  origin: z.string(),
  destination: z.string(),
  historicalAvgMins: z.number().positive(),
  standardDistanceKm: z.number().positive(),
  totalTripsCompleted: z.number().int().nonnegative(),
  status: RouteStatusSchema,
});

export type Route = z.infer<typeof RouteSchema>;
export type RouteStatus = z.infer<typeof RouteStatusSchema>;
