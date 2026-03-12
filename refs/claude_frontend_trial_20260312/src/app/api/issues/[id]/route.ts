import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { IssueSchema } from "@/lib/api/schemas";
import type { GetIssueResponse, ErrorResponse } from "@/lib/api/contracts";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<GetIssueResponse | ErrorResponse>> {
  const { id } = await params;
  const issue = dashboardConfig.issues.find((i) => i.id === id);

  if (!issue) {
    return NextResponse.json(
      { error: "Issue not found", code: "NOT_FOUND", timestamp: new Date().toISOString() },
      { status: 404 }
    );
  }

  const validated = IssueSchema.parse(issue);

  return NextResponse.json({
    data: validated,
    meta: { timestamp: new Date().toISOString() },
  });
}
