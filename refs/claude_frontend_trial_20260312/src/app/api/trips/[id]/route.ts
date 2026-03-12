import { NextResponse } from "next/server";
import { dashboardConfig } from "@/config/dashboard";
import { TripSchema } from "@/lib/api/schemas";
import type { GetTripResponse, ErrorResponse } from "@/lib/api/contracts";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ id: string }> }
): Promise<NextResponse<GetTripResponse | ErrorResponse>> {
  const { id } = await params;
  const trip = dashboardConfig.trips.find((t) => t.id === id);

  if (!trip) {
    return NextResponse.json(
      { error: "Trip not found", code: "NOT_FOUND", timestamp: new Date().toISOString() },
      { status: 404 }
    );
  }

  const validated = TripSchema.parse(trip);

  return NextResponse.json({
    data: validated,
    meta: { timestamp: new Date().toISOString() },
  });
}
