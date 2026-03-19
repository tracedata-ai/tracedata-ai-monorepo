"use client";

import { useCallback, useState } from "react";
import { AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getBackendHealth, type BackendHealth } from "@/lib/api";

export default function Home() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshHealth = useCallback(async () => {
    setLoading(true);
    const result = await getBackendHealth();
    setHealth(result);
    setLoading(false);
  }, []);

  const connected = health?.status === "ok";

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-4xl items-center px-4 py-10 sm:px-6 lg:px-8">
      <Card className="w-full">
        <CardHeader className="space-y-3">
          <CardTitle className="text-2xl">TraceData Frontend</CardTitle>
          <CardDescription>
            Next.js + Shadcn baseline with a simple api.ts abstraction.
          </CardDescription>
          <div className="flex items-center gap-2">
            {connected ? (
              <>
                <CheckCircle2 className="size-4 text-emerald-600" />
                <Badge className="bg-emerald-600 hover:bg-emerald-700">
                  Backend Connected
                </Badge>
              </>
            ) : (
              <>
                <AlertCircle className="size-4 text-amber-600" />
                <Badge variant="secondary">Mock Mode</Badge>
              </>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-md border p-4">
            <p className="text-sm text-muted-foreground">API base URL</p>
            <p className="font-mono text-sm">
              {health?.baseUrl ?? "(not set)"}
            </p>
          </div>

          <div className="rounded-md border p-4">
            <p className="text-sm text-muted-foreground">Status payload</p>
            <pre className="mt-2 overflow-x-auto text-xs">
              {JSON.stringify(health?.payload ?? {}, null, 2)}
            </pre>
          </div>

          <Button onClick={refreshHealth} disabled={loading} className="gap-2">
            <RefreshCw className={loading ? "size-4 animate-spin" : "size-4"} />
            {loading ? "Checking..." : "Check Backend"}
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
