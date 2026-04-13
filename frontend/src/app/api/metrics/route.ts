import { NextResponse } from "next/server";
import client from "prom-client";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const globalForMetrics = globalThis as typeof globalThis & {
  tracedataMetricsInit?: boolean;
};

if (!globalForMetrics.tracedataMetricsInit) {
  client.collectDefaultMetrics({ prefix: "tracedata_frontend_" });
  globalForMetrics.tracedataMetricsInit = true;
}

export async function GET(): Promise<NextResponse> {
  const body = await client.register.metrics();
  return new NextResponse(body, {
    status: 200,
    headers: { "Content-Type": client.register.contentType },
  });
}
