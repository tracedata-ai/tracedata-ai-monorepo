"use client";

import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function IssuesPage() {
  const stats = [
    { label: "Open Issues", value: "5", change: -2 },
    { label: "Critical", value: "1", change: 0 },
    { label: "Resolution Rate", value: "88%", change: 5 },
  ];

  return (
    <DashboardPageTemplate
      title="Issues & Incidents"
      subtitle="Track reported incidents and safety alerts"
      stats={stats}
    >
      <Card className="glass rounded-xl">
        <CardHeader>
          <CardTitle>Recent Incidents</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">Incidents loading...</p>
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
