"use client";

import React from "react";
import { BarChart3 } from "lucide-react";
import { DetailContentTemplate } from "@/components/shared/DetailContentTemplate";
import { BehaviorScoreBreakdown } from "@/components/explainability/BehaviorScoreBreakdown";
import { SHAPForcePlot } from "@/components/explainability/SHAPForcePlot";
import {
  mockTripScores,
  mockSHAPData,
  mockDriverBehavior,
} from "@/lib/mock-data";

interface DriverDetailSheetContentProps {
  driverId: string;
  driverName: string;
}

export function DriverDetailSheetContent({
  driverId,
  driverName,
}: DriverDetailSheetContentProps) {
  const behavior = mockDriverBehavior[driverId];

  // Helper to get trip data based on driverId
  // In a real app, this would be fetched based on the driverId
  const getLatestTripId = (id: string) => {
    if (id === "driver_alice_001") return "trip_20250310_001";
    if (id === "driver_bob_002") return "trip_20250310_002";
    return null;
  };

  const latestTripId = getLatestTripId(driverId);
  const tripScore = latestTripId ? mockTripScores[latestTripId] : null;
  const tripSHAP = latestTripId ? mockSHAPData[latestTripId] : null;

  return (
    <div className="space-y-6 px-6 pb-6">
      {/* Behavior Profile */}
      <div>
        <h4 className="font-semibold text-foreground mb-3">
          Behavior Profile
        </h4>
        {behavior ? (
          <DetailContentTemplate
            heroIcon={BarChart3}
            heroTitle={driverId}
            heroSubtitle="Driver ID"
            highlights={[
              {
                label: "Total Trips",
                value: behavior.totalTrips,
              },
              {
                label: "Avg Score",
                value: behavior.averageScore.toFixed(1),
              },
              {
                label: "Risk Incidents",
                value: behavior.totalRiskIncidents,
              },
              {
                label: "Burnout Risk",
                value: behavior.burnoutRiskLevel === 0 ? "Low" : "High",
                iconColor: behavior.burnoutRiskLevel === 0 ? "text-brand-teal" : "text-brand-red",
              },
            ]}
          >
            {/* Burnout indicators if high risk */}
            {behavior.burnoutRiskLevel === 1 && (
              <div className="rounded bg-red-50 p-3 text-sm text-red-800">
                <p className="font-semibold">Burnout Indicators</p>
                <ul className="mt-2 list-inside space-y-1 list-disc">
                  {behavior.burnoutIndicators.map((indicator, idx) => (
                    <li key={idx} className="text-sm">
                      {indicator}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </DetailContentTemplate>
        ) : (
          <div className="p-4 bg-muted/20 rounded-lg text-sm text-center text-muted-foreground">
            No behavior profile data available for this driver.
          </div>
        )}
      </div>

      {/* Latest Trip Score with XRAI */}
      {tripScore && (
        <div>
          <h4 className="font-semibold text-foreground mb-3">
            Latest Trip Score
          </h4>
          <BehaviorScoreBreakdown score={tripScore} />
        </div>
      )}

      {/* SHAP Force Plot */}
      {tripSHAP && (
        <div>
          <h4 className="font-semibold text-foreground mb-3">
            SHAP Explainability
          </h4>
          <SHAPForcePlot data={tripSHAP} />
        </div>
      )}
    </div>
  );
}
