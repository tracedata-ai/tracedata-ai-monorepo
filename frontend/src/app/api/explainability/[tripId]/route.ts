/**
 * API route: Get SHAP explainability data for a trip.
 * RUBRIC: XRAI—returns SHAP feature importance.
 * Reference: A5 (XGBoost Fairness & Explainability)
 */

import {
  isValidJWT,
  sanitizeTenantId,
  isValidTripId,
} from "@/lib/utils/security";
import { mockSHAPData } from "@/lib/mock-data";
import type { SHAPOutput } from "@/lib/types/explainability";

export async function GET(
  request: Request,
  { params }: { params: any },
) {
  try {
    // Validate tenant context
    const tenantId = request.headers.get("x-tenant-id");
    if (!tenantId) {
      return new Response(
        JSON.stringify({ error: "Tenant context required" }),
        { status: 403, headers: { "Content-Type": "application/json" } },
      );
    }

    const sanitized = sanitizeTenantId(tenantId);
    if (sanitized !== tenantId) {
      return new Response(
        JSON.stringify({ error: "Invalid tenant ID format" }),
        { status: 400, headers: { "Content-Type": "application/json" } },
      );
    }

    // Validate JWT
    const authHeader = request.headers.get("authorization");
    if (!authHeader?.startsWith("Bearer ")) {
      return new Response(
        JSON.stringify({ error: "Missing or invalid authorization header" }),
        { status: 401, headers: { "Content-Type": "application/json" } },
      );
    }

    const token = authHeader.slice(7);
    if (!isValidJWT(token)) {
      return new Response(JSON.stringify({ error: "Invalid JWT token" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Validate trip ID
    const tripId = params.tripId;
    if (!isValidTripId(tripId)) {
      return new Response(JSON.stringify({ error: "Invalid trip ID format" }), {
        status: 400,
        headers: { "Content-Type": "application/json" },
      });
    }

    // Get mock SHAP data
    const shapData = mockSHAPData[tripId] as SHAPOutput | undefined;
    if (!shapData) {
      return new Response(
        JSON.stringify({ error: "No SHAP data found for trip" }),
        { status: 404, headers: { "Content-Type": "application/json" } },
      );
    }

    return new Response(JSON.stringify(shapData), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("GET /api/explainability/shap/:tripId error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
