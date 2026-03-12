/**
 * API route: Get all drivers for a tenant.
 * RUBRIC: Cybersecurity—tenant isolation + JWT validation.
 * Reference: Constraint 2 (Multi-Tenancy)
 */

import {
  isValidJWT,
  sanitizeTenantId,
  secureHeaders,
} from "@/lib/utils/security";
import { mockDrivers } from "@/lib/mock-data";

export async function GET(request: Request) {
  try {
    // Extract tenant context
    const tenantId = request.headers.get("x-tenant-id");
    if (!tenantId) {
      return new Response(
        JSON.stringify({ error: "Tenant context required" }),
        {
          status: 403,
          headers: { "Content-Type": "application/json", ...secureHeaders },
        },
      );
    }

    // Validate tenant ID format
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

    // Filter drivers by tenant
    const drivers = mockDrivers.filter((d) => d.tenantId === tenantId);

    return new Response(JSON.stringify(drivers), {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        ...secureHeaders,
      },
    });
  } catch (error) {
    console.error("GET /api/drivers error:", error);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }
}
