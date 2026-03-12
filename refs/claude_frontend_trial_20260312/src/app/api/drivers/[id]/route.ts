import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { DriverSchema } from "@/lib/api/schemas";
import type { GetDriverResponse, ErrorResponse } from "@/lib/api/contracts";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<GetDriverResponse | ErrorResponse>> {
  const { id } = await params;
  const driver = dashboardConfig.drivers.find((d) => d.id === id);

  if (!driver) {
    return NextResponse.json(
      { error: "Driver not found", code: "NOT_FOUND", timestamp: new Date().toISOString() },
      { status: 404 }
    );
  }

  const validated = DriverSchema.parse(driver);

  return NextResponse.json({
    data: validated,
    meta: { timestamp: new Date().toISOString() },
  });
}
