import { z } from "zod";

export const VehicleStatusSchema = z.enum(["In Transit", "Charging", "Maintenance", "Idle"]);

export const SignalStrengthSchema = z.enum(["Strong", "Medium", "Weak"]);

export const VehicleSchema = z.object({
  id: z.string(),
  plateNumber: z.string(),
  model: z.string(),
  status: VehicleStatusSchema,
  operatingHours: z.number().nonnegative(),
  driver: z.string().optional(),
  location: z.string().optional(),
  signal: SignalStrengthSchema.optional(),
});

export type Vehicle = z.infer<typeof VehicleSchema>;
export type VehicleStatus = z.infer<typeof VehicleStatusSchema>;
export type SignalStrength = z.infer<typeof SignalStrengthSchema>;
