/**
 * Driver Trips Page - Shows driver's trip history
 */

"use client";

import React, { useState } from "react";
import { DashboardPageTemplate } from "@/components/shared/DashboardPageTemplate";
import { SHAPForcePlot } from "@/components/explainability/SHAPForcePlot";
import { BehaviorScoreBreakdown } from "@/components/explainability/BehaviorScoreBreakdown";
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
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Route, MapPin } from "lucide-react";
import { mockTripScores, mockSHAPData } from "@/lib/mock-data";

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
  const driverId = "driver_alice_001";

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

  const tripScore = selectedTrip ? mockTripScores[selectedTrip.id] : null;
  const tripSHAP = selectedTrip ? mockSHAPData[selectedTrip.id] : null;

  return (
    <DashboardPageTemplate
      title="My Trips"
      description="View your trip history and performance scores"
      breadcrumbs={
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <a href="/driver" className="hover:text-slate-700">
            Dashboard
          </a>
          <span>/</span>
          <span>Trips</span>
        </div>
      }
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
        {/* Trips Table */}
        <section className="rounded-lg border border-slate-200 overflow-hidden">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50">
                  <TableHead className="font-bold text-foreground">
                    Date
                  </TableHead>
                  <TableHead className="font-bold text-foreground">
                    Route
                  </TableHead>
                  <TableHead className="font-bold text-foreground">
                    Distance
                  </TableHead>
                  <TableHead className="font-bold text-foreground">
                    Score
                  </TableHead>
                  <TableHead className="font-bold text-foreground">
                    Risk
                  </TableHead>
                  <TableHead className="font-bold text-foreground">
                    Action
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {MOCK_DRIVER_TRIPS.map((trip) => (
                  <TableRow key={trip.id} className="hover:bg-slate-50">
                    <TableCell className="text-sm font-mono">
                      {new Date(trip.date).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="text-sm">
                      <div className="flex flex-col gap-1">
                        <span className="font-medium">{trip.from}</span>
                        <span className="text-xs text-muted-foreground">
                          → {trip.to}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell className="text-sm">
                      {trip.distance} mi
                    </TableCell>
                    <TableCell className="text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                            trip.score >= 80
                              ? "bg-green-100 text-green-900"
                              : trip.score >= 70
                                ? "bg-yellow-100 text-yellow-900"
                                : "bg-red-100 text-red-900"
                          }`}
                        >
                          {trip.score}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getRiskColor(trip.riskLevel)}>
                        {getRiskLabel(trip.riskLevel)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => setSelectedTrip(trip)}
                        className="text-brand-blue hover:text-brand-blue/90"
                      >
                        Details
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>
      </div>

      {/* Detail Sheet */}
      <Sheet open={!!selectedTrip} onOpenChange={() => setSelectedTrip(null)}>
        <SheetContent className="w-full max-w-2xl overflow-y-auto">
          {selectedTrip && tripScore && tripSHAP && (
            <>
              <SheetHeader>
                <SheetTitle>Trip Details</SheetTitle>
                <SheetDescription>
                  {selectedTrip.from} → {selectedTrip.to}
                </SheetDescription>
              </SheetHeader>

              <div className="space-y-8 mt-6">
                {/* Trip Info */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-foreground">
                    Trip Information
                  </h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground text-xs uppercase tracking-wider font-bold">
                        Date
                      </p>
                      <p className="font-mono">
                        {new Date(selectedTrip.date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs uppercase tracking-wider font-bold">
                        Duration
                      </p>
                      <p className="font-mono">{selectedTrip.duration} min</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs uppercase tracking-wider font-bold">
                        Distance
                      </p>
                      <p className="font-mono">{selectedTrip.distance} miles</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs uppercase tracking-wider font-bold">
                        Risk Level
                      </p>
                      <Badge className={getRiskColor(selectedTrip.riskLevel)}>
                        {getRiskLabel(selectedTrip.riskLevel)}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Score Breakdown */}
                <BehaviorScoreBreakdown score={tripScore} />

                {/* SHAP Explanation */}
                <SHAPForcePlot data={tripSHAP} />

                {/* Appeal Option */}
                <div className="border-t pt-4">
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => setSelectedTrip(null)}
                  >
                    Dispute or Appeal This Trip
                  </Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </DashboardPageTemplate>
  );
}
