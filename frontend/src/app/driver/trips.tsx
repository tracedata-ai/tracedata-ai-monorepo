/**
 * Driver Trips Page - Shows driver's trip history
 */

"use client";

import React, { useState } from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { SHAPForcePlot } from "@/components/explainability/SHAPForcePlot";
import { BehaviorScoreBreakdown } from "@/components/explainability/BehaviorScoreBreakdown";
import { useAuth } from "@/context/AuthContext";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Route, MapPin } from "lucide-react";
import { mockTripScores, mockSHAPData } from "@/lib/mock-data";
import { DataTable } from "@/components/shared/data-table";
import { DetailSheet } from "@/components/shared/detail-sheet";
import { ColumnDef } from "@tanstack/react-table";

// Mock driver trips
const MOCK_DRIVER_TRIPS = [
  {
    id: "trip_20250310_001",
    date: "2025-03-10",
    from: "Downtown Hub",
    to: "Airport Terminal",
    distance: 12.5,
    duration: 34,
    score: 85,
    riskLevel: "low",
  },
  {
    id: "trip_20250309_002",
    date: "2025-03-09",
    from: "Central Station",
    to: "Harbor District",
    distance: 8.3,
    duration: 22,
    score: 78,
    riskLevel: "medium",
  },
  {
    id: "trip_20250308_003",
    date: "2025-03-08",
    from: "Airport Terminal",
    to: "Downtown Hub",
    distance: 13.1,
    duration: 36,
    score: 92,
    riskLevel: "low",
  },
  {
    id: "trip_20250307_004",
    date: "2025-03-07",
    from: "Business Park",
    to: "Waterfront",
    distance: 7.2,
    duration: 18,
    score: 68,
    riskLevel: "high",
  },
];

export default function DriverTrips() {
  const [selectedTrip, setSelectedTrip] = useState<
    (typeof MOCK_DRIVER_TRIPS)[0] | null
  >(null);
  const { role } = useAuth();

  const getRiskColor = (level: string) => {
    switch (level) {
      case "low":
        return "bg-green-100 text-green-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "high":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getRiskLabel = (level: string) => {
    switch (level) {
      case "low":
        return "Safe";
      case "medium":
        return "Caution";
      case "high":
        return "Alert";
      default:
        return "Unknown";
    }
  };

  const columns: ColumnDef<(typeof MOCK_DRIVER_TRIPS)[0]>[] = [
    {
      accessorKey: "date",
      header: "Date",
      cell: ({ row }) => (
        <span className="text-sm font-mono">
          {new Date(row.original.date).toLocaleDateString()}
        </span>
      ),
    },
    {
      accessorKey: "from",
      header: "Route",
      cell: ({ row }) => (
        <div className="flex flex-col gap-1 text-left">
          <span className="font-medium text-sm">{row.original.from}</span>
          <span className="text-xs text-muted-foreground">
            → {row.original.to}
          </span>
        </div>
      ),
    },
    {
      accessorKey: "distance",
      header: "Distance",
      cell: ({ row }) => <span className="text-sm">{row.original.distance} mi</span>,
    },
    {
      accessorKey: "score",
      header: "Score",
      cell: ({ row }) => (
        <div className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
              row.original.score >= 80
                ? "bg-green-100 text-green-900"
                : row.original.score >= 70
                  ? "bg-yellow-100 text-yellow-900"
                  : "bg-red-100 text-red-900"
            }`}
          >
            {row.original.score}
          </div>
        </div>
      ),
    },
    {
      accessorKey: "riskLevel",
      header: "Risk",
      cell: ({ row }) => (
        <Badge className={getRiskColor(row.original.riskLevel)}>
          {getRiskLabel(row.original.riskLevel)}
        </Badge>
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
            setSelectedTrip(row.original);
          }}
          className="text-brand-blue hover:text-brand-blue/90 font-bold"
        >
          Details
        </Button>
      ),
    },
  ];

  const tripScore = selectedTrip ? mockTripScores[selectedTrip.id] : null;
  const tripSHAP = selectedTrip ? mockSHAPData[selectedTrip.id] : null;

  return (
    <DashboardPageTemplate
      title="My Trips"
      description="View your trip history and performance scores"
      stats={
        <>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <Route className="w-5 h-5 text-brand-blue" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Total Trips
                </p>
                <p className="text-2xl font-black text-foreground">
                  {MOCK_DRIVER_TRIPS.length}
                </p>
              </div>
            </div>
          </div>
          <div className="glass-card rounded-xl p-4">
            <div className="flex items-center gap-3">
              <MapPin className="w-5 h-5 text-brand-teal" />
              <div>
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  Distance
                </p>
                <p className="text-2xl font-black text-foreground">
                  {MOCK_DRIVER_TRIPS.reduce(
                    (sum, t) => sum + t.distance,
                    0,
                  ).toFixed(1)}{" "}
                  mi
                </p>
              </div>
            </div>
          </div>
        </>
      }
    >
      <div className="space-y-6">
        <DataTable
          columns={columns}
          data={MOCK_DRIVER_TRIPS}
          onRowClick={(trip) => setSelectedTrip(trip)}
          selectedId={selectedTrip?.id}
        />
      </div>

      <DetailSheet
        open={!!selectedTrip}
        onOpenChange={(open) => !open && setSelectedTrip(null)}
        title="Trip Details"
      >
        {selectedTrip && tripScore && tripSHAP && (
          <div className="space-y-8 px-6 pb-6 mt-4">
            <div>
              <h3 className="font-semibold text-foreground mb-3">
                Trip Information
              </h3>
              <div className="grid grid-cols-2 gap-4 text-sm bg-muted/20 p-4 rounded-lg">
                <div>
                  <p className="text-muted-foreground text-[10px] uppercase tracking-wider font-bold">
                    Date
                  </p>
                  <p className="font-mono font-bold">
                    {new Date(selectedTrip.date).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground text-[10px] uppercase tracking-wider font-bold">
                    Duration
                  </p>
                  <p className="font-mono font-bold">{selectedTrip.duration} min</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-[10px] uppercase tracking-wider font-bold">
                    Distance
                  </p>
                  <p className="font-mono font-bold">{selectedTrip.distance} miles</p>
                </div>
                <div>
                  <p className="text-muted-foreground text-[10px] uppercase tracking-wider font-bold mb-1">
                    Risk Level
                  </p>
                  <Badge className={`${getRiskColor(selectedTrip.riskLevel)} font-bold`}>
                    {getRiskLabel(selectedTrip.riskLevel)}
                  </Badge>
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-foreground mb-3 uppercase tracking-tight text-xs">Behavioral Score Breakdown</h3>
              <BehaviorScoreBreakdown score={tripScore} />
            </div>

            <div>
              <h3 className="font-semibold text-foreground mb-3 uppercase tracking-tight text-xs">Feature Importance (SHAP)</h3>
              <SHAPForcePlot data={tripSHAP} />
            </div>

            <div className="border-t pt-6">
              <Button
                variant="outline"
                className="w-full font-bold border-brand-blue text-brand-blue hover:bg-brand-blue/10"
                onClick={() => setSelectedTrip(null)}
              >
                Dispute or Appeal This Trip
              </Button>
            </div>
          </div>
        )}
      </DetailSheet>
    </DashboardPageTemplate>
  );
}
