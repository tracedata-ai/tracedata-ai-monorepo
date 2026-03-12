/**
 * Driver Appeals Page - Dispute and appeal scoring decisions
 */

"use client";

import React, { useState } from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { useAuth } from "@/context/AuthContext";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle2 } from "lucide-react";

// Mock appeals
const MOCK_DRIVER_APPEALS = [
  {
    id: "appeal_001",
    tripId: "trip_20250307_004",
    status: "pending",
    score: 68,
    reason: "Sudden traffic light change",
    createdAt: "2025-03-10",
    lastUpdated: "2025-03-10",
    notes:
      "I was traveling at normal speed when the traffic light turned red without warning.",
  },
  {
    id: "appeal_002",
    tripId: "trip_20250309_002",
    status: "approved",
    score: 78,
    reason: "Aggressive driver cut me off",
    createdAt: "2025-03-09",
    lastUpdated: "2025-03-09",
    notes:
      "Another vehicle merged into my lane without signaling. I had to brake suddenly.",
    reviewerNote:
      "Telemetry confirmed external vehicle behavior. Appeal approved.",
  },
];

import { DataTable } from "@/components/shared/data-table";
import { ColumnDef } from "@tanstack/react-table";

// ... (existing helper functions getStatusColor and getStatusLabel kept as is)

export default function DriverAppeals() {
  const [selectedAppeal, setSelectedAppeal] = useState<
    (typeof MOCK_DRIVER_APPEALS)[0] | null
  >(null);
  const [newNote, setNewNote] = useState("");

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800";
      case "rejected":
        return "bg-red-100 text-red-800";
      case "pending":
        return "bg-yellow-100 text-yellow-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case "approved":
        return "✓ Approved";
      case "rejected":
        return "✗ Rejected";
      case "pending":
        return "⏱ Pending";
      default:
        return "Unknown";
    }
  };

  const columns: ColumnDef<(typeof MOCK_DRIVER_APPEALS)[0]>[] = [
    {
      accessorKey: "tripId",
      header: "Trip ID",
      cell: ({ row }) => <span className="text-sm font-mono">{row.original.tripId}</span>,
    },
    {
      accessorKey: "reason",
      header: "Reason",
      cell: ({ row }) => <span className="text-sm">{row.original.reason}</span>,
    },
    {
      accessorKey: "score",
      header: "Score",
      cell: ({ row }) => (
        <div
          className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-bold ${
            row.original.score >= 80
              ? "bg-green-100 text-green-900"
              : row.original.score >= 70
                ? "bg-yellow-100 text-yellow-900"
                : "bg-red-100 text-red-900"
          }`}
        >
          {row.original.score}
        </div>
      ),
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => (
        <Badge className={getStatusColor(row.original.status)}>
          {getStatusLabel(row.original.status)}
        </Badge>
      ),
    },
    {
      accessorKey: "createdAt",
      header: "Date",
      cell: ({ row }) => (
        <span className="text-sm text-muted-foreground">{row.original.createdAt}</span>
      ),
    },
    {
      id: "actions",
      header: "Action",
      cell: ({ row }) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            setSelectedAppeal(row.original);
          }}
          className="text-brand-blue hover:text-brand-blue/90"
        >
          Review
        </Button>
      ),
    },
  ];

  return (
    <DashboardPageTemplate
      title="Appeals & Disputes"
      description="Review and manage your appeals"
      // ... (stats remained unchanged)
      stats={
        <>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 text-brand-rose" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Total Appeals
                </p>
                <p className="text-2xl font-black text-foreground">
                  {MOCK_DRIVER_APPEALS.length}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-5 h-5 text-brand-teal" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Approved
                </p>
                <p className="text-2xl font-black text-foreground">
                  {
                    MOCK_DRIVER_APPEALS.filter((a) => a.status === "approved")
                      .length
                  }
                </p>
              </div>
            </div>
          </div>
        </>
      }
    >
      <div className="space-y-6">
        {/* Appeals Table */}
        <DataTable
          columns={columns}
          data={MOCK_DRIVER_APPEALS}
          onRowClick={(appeal) => setSelectedAppeal(appeal)}
          selectedId={selectedAppeal?.id}
        />

        {/* No Appeals Info */}
        {MOCK_DRIVER_APPEALS.length === 0 && (
          <div className="rounded-lg bg-green-50 border border-green-200 p-6 text-center">
            <CheckCircle2 className="w-12 h-12 text-green-600 mx-auto mb-3" />
            <p className="font-semibold text-green-900">No Appeals</p>
            <p className="text-sm text-green-800 mt-1">
              You haven't submitted any appeals. If you disagree with a trip
              score, you can dispute it from the trip details.
            </p>
          </div>
        )}
      </div>

      {/* Appeal Detail Sheet */}
      <Sheet
        open={!!selectedAppeal}
        onOpenChange={() => setSelectedAppeal(null)}
      >
        <SheetContent className="w-full max-w-2xl overflow-y-auto">
          {selectedAppeal && (
            <>
              <SheetHeader>
                <SheetTitle>Appeal Details</SheetTitle>
                <SheetDescription>{selectedAppeal.tripId}</SheetDescription>
              </SheetHeader>

              <div className="space-y-6 mt-6">
                {/* Appeal Summary */}
                <div className="rounded bg-slate-50 p-4 space-y-3">
                  <div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Status
                    </p>
                    <Badge
                      className={`mt-1 ${getStatusColor(selectedAppeal.status)}`}
                    >
                      {getStatusLabel(selectedAppeal.status)}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Original Score
                    </p>
                    <div
                      className={`inline-flex items-center justify-center w-10 h-10 rounded-full text-sm font-bold mt-1 ${
                        selectedAppeal.score >= 80
                          ? "bg-green-100 text-green-900"
                          : selectedAppeal.score >= 70
                            ? "bg-yellow-100 text-yellow-900"
                            : "bg-red-100 text-red-900"
                      }`}
                    >
                      {selectedAppeal.score}
                    </div>
                  </div>
                  <div>
                    <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                      Reason for Appeal
                    </p>
                    <p className="text-sm mt-1 font-medium">
                      {selectedAppeal.reason}
                    </p>
                  </div>
                </div>

                {/* Your Statement */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-foreground">
                    Your Statement
                  </h3>
                  <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm">
                    {selectedAppeal.notes}
                  </div>
                </div>

                {/* Reviewer Response (if available) */}
                {selectedAppeal.status !== "pending" &&
                  selectedAppeal.reviewerNote && (
                    <div className="space-y-3">
                      <h3 className="font-semibold text-foreground">
                        Review Decision
                      </h3>
                      <div className="bg-purple-50 border border-purple-200 rounded p-3 text-sm">
                        {selectedAppeal.reviewerNote}
                      </div>
                    </div>
                  )}

                {/* Additional Notes (if pending) */}
                {selectedAppeal.status === "pending" && (
                  <div className="space-y-3">
                    <h3 className="font-semibold text-foreground">
                      Add Additional Context
                    </h3>
                    <Textarea
                      placeholder="Please provide any additional information that might help with your appeal..."
                      value={newNote}
                      onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setNewNote(e.target.value)}
                      className="min-h-24"
                    />
                    <Button className="w-full bg-brand-blue hover:bg-brand-blue/90">
                      Submit Additional Information
                    </Button>
                  </div>
                )}

                {/* Timeline */}
                <div className="space-y-3 border-t pt-4">
                  <h3 className="font-semibold text-foreground text-sm">
                    Timeline
                  </h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Submitted</span>
                      <span className="font-mono">
                        {selectedAppeal.createdAt}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">
                        Last Updated
                      </span>
                      <span className="font-mono">
                        {selectedAppeal.lastUpdated}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </DashboardPageTemplate>
  );
}
