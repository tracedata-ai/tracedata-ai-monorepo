import Link from "next/link";
import { BrandMark } from "@/components/shared/BrandMark";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[var(--gray-50)] to-[var(--gray-100)] flex items-center justify-center p-4">
      <div className="max-w-4xl w-full space-y-10">
        <div className="text-center space-y-5">
          <div className="flex justify-center">
            <BrandMark size={64} priority />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-foreground">
            TraceData Fleet Console
          </h1>
          <p className="text-lg text-muted-foreground">
            AI-powered fleet visibility, driver safety insights, and real-time
            telemetry orchestration.
          </p>
          <div className="flex justify-center gap-3 pt-2">
            <Link href="/login">
              <Button className="bg-[var(--info)] text-white hover:bg-[hsl(210_100%_45%)]">
                Open Login
              </Button>
            </Link>
            <Link href="/fleet-manager">
              <Button variant="outline" className="border-[var(--info)]/40">
                View Demo Dashboard
              </Button>
            </Link>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Card className="glass rounded-xl p-6">
            <h2 className="text-lg font-bold text-foreground mb-2">
              Fleet Managers
            </h2>
            <p className="text-sm text-muted-foreground">
              Monitor routes, trips, driver safety, and real-time telemetry.
              Optimize operations with comprehensive analytics.
            </p>
          </Card>

          <Card className="glass rounded-xl p-6">
            <h2 className="text-lg font-bold text-foreground mb-2">Drivers</h2>
            <p className="text-sm text-muted-foreground">
              View current trips, check fatigue levels, and access support. Stay
              informed with real-time alerts.
            </p>
          </Card>
        </div>

        <Card className="glass rounded-xl p-6 md:p-8">
          <h3 className="text-xl font-bold tracking-tight text-foreground">
            Platform Highlights
          </h3>
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="rounded-lg bg-white/40 p-4">
              <p className="font-semibold">Live Operations</p>
              <p className="text-muted-foreground mt-1">
                Monitor route health, delays, and incident flow in one place.
              </p>
            </div>
            <div className="rounded-lg bg-white/40 p-4">
              <p className="font-semibold">Driver Safety</p>
              <p className="text-muted-foreground mt-1">
                Track fatigue risk and behavior indicators across active trips.
              </p>
            </div>
            <div className="rounded-lg bg-white/40 p-4">
              <p className="font-semibold">Telemetry Insights</p>
              <p className="text-muted-foreground mt-1">
                Capture event streams and investigate anomalies in real time.
              </p>
            </div>
          </div>
        </Card>

        <div className="text-center text-sm text-muted-foreground pt-8">
          <p>
            © 2026 TraceData. All rights reserved. |{" "}
            <a href="#" className="hover:text-foreground transition-colors">
              Privacy
            </a>{" "}
            •{" "}
            <a href="#" className="hover:text-foreground transition-colors">
              Terms
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
