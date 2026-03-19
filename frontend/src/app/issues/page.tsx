"use client";

import type { ColumnDef } from "@tanstack/react-table";

import { DataTable } from "@/components/data-table";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { issueRows, type IssueRow } from "@/lib/sample-data";

const columns: ColumnDef<IssueRow>[] = [
  { accessorKey: "id", header: "Issue ID" },
  {
    accessorKey: "severity",
    header: "Severity",
    cell: ({ row }) => {
      const severity = row.original.severity;
      const className =
        severity === "High"
          ? "bg-red-600 hover:bg-red-700"
          : severity === "Medium"
            ? "bg-amber-500 hover:bg-amber-600"
            : "bg-slate-600 hover:bg-slate-700";
      return <Badge className={className}>{severity}</Badge>;
    },
  },
  { accessorKey: "category", header: "Category" },
  { accessorKey: "driver", header: "Driver" },
  { accessorKey: "routeName", header: "Route" },
  { accessorKey: "createdAt", header: "Created At" },
];

export default function IssuesPage() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Issues</CardTitle>
      </CardHeader>
      <CardContent>
        <DataTable columns={columns} data={issueRows} />
      </CardContent>
    </Card>
  );
}
