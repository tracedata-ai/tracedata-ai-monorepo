import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { IssueSchema } from "@/lib/api/schemas";
import type { ListIssuesResponse } from "@/lib/api/contracts";
import { z } from "zod";

export async function GET(): Promise<NextResponse<ListIssuesResponse>> {
  const validated = z.array(IssueSchema).parse(dashboardConfig.issues);

  return NextResponse.json({
    data: validated,
    meta: {
      total: validated.length,
      timestamp: new Date().toISOString(),
    },
  });
}
