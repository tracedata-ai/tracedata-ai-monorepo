import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { VehicleSchema } from "@/lib/api/schemas";
import type { ListFleetResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListFleetResponse>> {
  const validated = z.array(VehicleSchema).parse(dashboardConfig.vehicles);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
