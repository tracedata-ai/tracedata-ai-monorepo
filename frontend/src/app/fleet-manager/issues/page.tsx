"use client";

import { useEffect, useState } from "react";
import { getIssues } from "@/lib/api";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DataTable } from "@/components/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const columns: ColumnDef<any>[] = [
  {
    accessorKey: "event_type",
    header: "Type",
    cell: (info) => (info.getValue() as string).replace("_", " "),
  },
  {
    accessorKey: "severity",
    header: "Severity",
    cell: (info) => {
      const severity = info.getValue() as string;
      const variant = {
        critical: "bg-red-600",
        high: "bg-orange-500",
        medium: "bg-yellow-500",
        low: "bg-blue-500",
      }[severity] || "bg-gray-500";
      return <Badge className={`${variant} text-white`}>{severity}</Badge>;
    },
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "created_at",
    header: "Detected At",
    cell: (info) => new Date(info.getValue() as string).toLocaleString(),
  },
];

export default function IssuesPage() {
  const [issues, setIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadIssues() {
      try {
        const data = await getIssues();
        setIssues(data);
      } catch (error) {
        console.error("Failed to fetch issues:", error);
      } finally {
        setLoading(false);
      }
    }
    loadIssues();
  }, []);

  const stats = [
    { label: "Total Issues", value: loading ? "..." : issues.length.toString(), change: -2 },
    { label: "Critical", value: loading ? "..." : issues.filter(i => i.severity === "critical").length.toString(), change: 0 },
    { label: "High Severity", value: loading ? "..." : issues.filter(i => i.severity === "high").length.toString(), change: 1 },
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
          {loading ? (
            <div className="space-y-4">
              <Skeleton className="h-10 w-full" />
              <Skeleton className="h-10 w-full" />
            </div>
          ) : (
            <DataTable columns={columns} data={issues} />
          )}
        </CardContent>
      </Card>
    </DashboardPageTemplate>
  );
}
