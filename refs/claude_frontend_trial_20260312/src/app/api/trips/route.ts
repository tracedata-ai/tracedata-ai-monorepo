import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { TripSchema } from "@/lib/api/schemas";
import type { ListTripsResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListTripsResponse>> {
  const validated = z.array(TripSchema).parse(dashboardConfig.trips);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
