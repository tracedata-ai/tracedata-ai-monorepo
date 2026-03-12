import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { AgentSchema } from "@/lib/api/schemas";
import type { ListAgentsResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListAgentsResponse>> {
  const validated = z.array(AgentSchema).parse(dashboardConfig.agents);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
