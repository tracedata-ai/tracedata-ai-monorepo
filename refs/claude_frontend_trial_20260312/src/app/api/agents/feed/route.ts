import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { OrchestrationEventSchema } from "@/lib/api/schemas";
import type { ListOrchestrationFeedResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListOrchestrationFeedResponse>> {
  const validated = z.array(OrchestrationEventSchema).parse(dashboardConfig.orchestrationFeed);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
