"use client";

import { DataTable } from "@/components/shared/DataTable";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { UsersIcon, UserCheckIcon } from "lucide-react";

type Driver = {
  id: string;
  name: string;
  license: string;
  rating: number;
  status: "available" | "on-trip" | "offline";
  avatar?: string;
};

const columns: ColumnDef<Driver>[] = [
  {
    accessorKey: "name",
    header: "Driver",
    cell: ({ row }) => {
      const name = row.getValue("name") as string;
      const avatar = row.original.avatar;
      return (
        <div className="flex items-center gap-3">
          <Avatar className="h-9 w-9 border border-border shadow-sm">
            <AvatarImage src={avatar} alt={name} />
            <AvatarFallback className="bg-slate-100 text-slate-500 font-bold text-xs">
              {name.split(" ").map(n => n[0]).join("")}
            </AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <span className="font-semibold text-slate-900 leading-none mb-1">{name}</span>
            <span className="text-[10px] text-muted-foreground font-medium uppercase tracking-tighter">Verified Professional</span>
          </div>
        </div>
      );
    },
  },
  {
    accessorKey: "license",
    header: "License No.",
    cell: ({ row }) => <code className="text-[11px] font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600 border border-slate-200">{row.getValue("license")}</code>,
  },
  {
    accessorKey: "rating",
    header: "Rating",
    cell: ({ row }) => {
      const rating = row.getValue("rating") as number;
      return (
        <div className="flex items-center gap-1">
          <span className="text-yellow-500 text-xs">★</span>
          <span className="font-bold text-slate-700">{rating.toFixed(1)}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as string;
      return (
        <Badge 
          variant={status === "available" ? "default" : status === "on-trip" ? "secondary" : "outline"}
          className={cn(
            "capitalize font-semibold text-[10px] px-2 py-0",
            status === "available" && "bg-slate-700 text-white",
            status === "on-trip" && "bg-slate-100 text-slate-700",
            status === "offline" && "text-slate-400 bg-slate-50"
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
      <div className="flex flex-col gap-1">
        <h2 className="text-2xl font-bold text-slate-900">Personnel</h2>
        <p className="text-slate-500">Manage driver credentials, ratings, and real-time availability.</p>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <UsersIcon className="w-4 h-4" />
              Total Workforce
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">{data.length}</div>
          </CardContent>
        </Card>

        <Card className="border shadow-none">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-xs uppercase tracking-wider text-slate-500 font-bold flex items-center gap-2">
              <UserCheckIcon className="w-4 h-4" />
              Available Now
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0">
            <div className="text-2xl font-bold text-slate-900">
              {data.filter(d => d.status === "available").length}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="border rounded-lg p-1 bg-white">
        <DataTable columns={columns} data={data} filterKey="name" />
      </div>
    </div>
  );
}
