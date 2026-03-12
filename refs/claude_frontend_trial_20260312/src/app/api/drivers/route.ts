import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { DriverSchema } from "@/lib/api/schemas";
import type { ListDriversResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListDriversResponse>> {
  const validated = z.array(DriverSchema).parse(dashboardConfig.drivers);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
