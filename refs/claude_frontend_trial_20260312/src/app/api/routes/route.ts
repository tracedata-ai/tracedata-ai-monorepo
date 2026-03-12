import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { RouteSchema } from "@/lib/api/schemas";
import type { ListRoutesResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListRoutesResponse>> {
  const validated = z.array(RouteSchema).parse(dashboardConfig.routes);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
