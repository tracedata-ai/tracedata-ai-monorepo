import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { VehicleSchema } from "@/lib/api/schemas";
import type { GetVehicleResponse, ErrorResponse } from "@/lib/api/contracts";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<GetVehicleResponse | ErrorResponse>> {
  const { id } = await params;
  const vehicle = dashboardConfig.vehicles.find((v) => v.id === id);

  if (!vehicle) {
    return NextResponse.json(
      { error: "Vehicle not found", code: "NOT_FOUND", timestamp: new Date().toISOString() },
      { status: 404 }
    );
  }

  const validated = VehicleSchema.parse(vehicle);

  return NextResponse.json({
    data: validated,
    meta: { timestamp: new Date().toISOString() },
  });
}
