import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { RouteSchema } from "@/lib/api/schemas";
import type { GetRouteResponse, ErrorResponse } from "@/lib/api/contracts";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<GetRouteResponse | ErrorResponse>> {
  const { id } = await params;
  const route = dashboardConfig.routes.find((r) => r.id === id);

  if (!route) {
    return NextResponse.json(
      { error: "Route not found", code: "NOT_FOUND", timestamp: new Date().toISOString() },
      { status: 404 }
    );
  }

  const validated = RouteSchema.parse(route);

  return NextResponse.json({
    data: validated,
    meta: { timestamp: new Date().toISOString() },
  });
}
