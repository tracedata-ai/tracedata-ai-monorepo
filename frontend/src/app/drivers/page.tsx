"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type Driver = {
  id: string;
  name: string;
  license: string;
  rating: number;
  status: "available" | "on-trip" | "offline";
};

const columns: ColumnDef<Driver>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "license",
    header: "License No.",
  },
  {
    accessorKey: "rating",
    header: "Rating",
    cell: ({ row }) => {
      const rating = row.getValue("rating") as number;
      return <span className="font-medium">⭐ {rating.toFixed(1)}</span>;
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge 
          variant="outline"
          className={cn(
            "capitalize border-2",
            status === "available" && "border-brand-teal text-brand-teal",
            status === "on-trip" && "border-brand-blue text-brand-blue",
            status === "offline" && "border-muted-foreground text-muted-foreground"
          )}
        >
          {status}
        </Badge>
      );
    },
  },
];

const data: Driver[] = [
  { id: "D-501", name: "Alex Chen", license: "S1234567A", rating: 4.8, status: "on-trip" },
  { id: "D-502", name: "Sarah Lim", license: "S7654321B", rating: 4.9, status: "on-trip" },
  { id: "D-503", name: "Michael Tan", license: "S9876543C", rating: 4.5, status: "available" },
  { id: "D-504", name: "Priya Singh", license: "S1122334D", rating: 4.7, status: "available" },
  { id: "D-505", name: "David Wong", license: "S4433221E", rating: 4.2, status: "offline" },
];

export default function DriversPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h2 className="text-3xl font-bold tracking-tight">Drivers</h2>
        <p className="text-muted-foreground">Manage driver profiles and performance.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Total Drivers</h3>
          <p className="text-3xl font-bold text-brand-blue">{data.length}</p>
        </div>
        <div className="p-6 glass-card rounded-xl border border-border/50">
          <h3 className="font-semibold text-lg mb-2">Available</h3>
          <p className="text-3xl font-bold text-brand-teal">
            {data.filter(d => d.status === "available").length}
          </p>
        </div>
      </div>

      <DataTable columns={columns} data={data} filterKey="name" />
    </div>
  );
}
