"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function DriverDashboard() {
  const stats = [
    { label: "Current Status", value: "On Duty" },
    { label: "Hours This Week", value: "32h 15m", change: 4 },
    { label: "Fatigue Level", value: "Low" },
    { label: "Safety Score", value: "9.2/10", change: 0.1 },
  ];

  return (
    <DashboardPageTemplate
      title="Driver Portal"
      subtitle="Your current trips, performance metrics, and alerts"
      stats={stats}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg">Current Trip</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">Route</p>
              <p className="font-semibold text-foreground">
                NY-BOS: New York to Boston
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Distance Remaining
              </p>
              <p className="font-semibold text-foreground">125 km (1h 45min)</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Status</p>
              <Badge className="bg-[var(--info)] text-white">In Progress</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg">Fatigue Assessment</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Hours Driven Today
              </p>
              <p className="font-semibold text-foreground">6h 30m</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">
                Recommended Rest
              </p>
              <p className="font-semibold text-foreground">Not Required</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">Risk Level</p>
              <Badge className="bg-[var(--success)] text-white">Low</Badge>
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg">
              This Week&apos;s Performance
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">
                Trips Completed
              </span>
              <span className="font-semibold text-foreground">8</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">
                On-Time Delivery
              </span>
              <span className="font-semibold text-foreground">100%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">
                Distance Covered
              </span>
              <span className="font-semibold text-foreground">1,240 km</span>
            </div>
          </CardContent>
        </Card>

        <Card className="glass rounded-xl">
          <CardHeader>
            <CardTitle className="text-lg">Safety Alerts</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3">
              <Badge className="bg-[var(--success)] text-white text-xs">
                ✓
              </Badge>
              <p className="text-sm text-foreground">
                No harsh braking detected
              </p>
            </div>
            <div className="flex items-start gap-3">
              <Badge className="bg-[var(--success)] text-white text-xs">
                ✓
              </Badge>
              <p className="text-sm text-foreground">Speed compliant</p>
            </div>
            <div className="flex items-start gap-3">
              <Badge className="bg-[var(--success)] text-white text-xs">
                ✓
              </Badge>
              <p className="text-sm text-foreground">No lane departures</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardPageTemplate>
  );
}
