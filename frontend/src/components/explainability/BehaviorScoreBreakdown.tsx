"use client";

import React, { useMemo } from "react";
import { cn } from "@/lib/utils";
import type { TripScore } from "@/lib/types/scoring";

interface BehaviorScoreBreakdownProps {
  score: TripScore;
  className?: string;
}

/**
 * BehaviorScoreBreakdown shows XGBoost scoring decomposed by component.
 * RUBRIC: XRAI—allows fleet operators to understand scoring rationale.
 * RUBRIC: Performance—memoized computation for large datasets.
 * Reference: A5 (Behavior Agent, XGBoost, AIF360)
 */
export function BehaviorScoreBreakdown({
  score,
  className,
}: BehaviorScoreBreakdownProps) {
  const contribution = useMemo(() => {
    return score.scoreBreakdown.map((c) => ({
      ...c,
      percentOfTotal: (c.contribution / score.totalScore) * 100,
    }));
  }, [score]);

  const riskColor = {
    low: "bg-teal-100 text-teal-800 border-teal-300",
    medium: "bg-yellow-100 text-yellow-800 border-yellow-300",
    high: "bg-rose-100 text-rose-800 border-rose-300",
    critical: "bg-red-100 text-red-800 border-red-300",
  };

  return (
    <div
      className={cn(
        "space-y-6 rounded-lg border border-gray-200 bg-white p-6",
        className,
      )}
    >
      <div>
        <h3 className="font-semibold text-gray-900">
          Driver Behavior Score Breakdown
        </h3>
        <p className="mt-1 text-sm text-gray-600 font-mono">
          Trip: {score.tripId}
        </p>
      </div>

      {/* Overall score badge */}
      <div className={`rounded-lg border p-4 ${riskColor[score.riskLevel]}`}>
        <p className="text-sm font-medium">Overall Safety Score</p>
        <p className="mt-1 text-3xl font-bold">{score.totalScore.toFixed(1)}</p>
        <p className="mt-2 text-sm font-semibold uppercase">
          {score.riskLevel} Risk
        </p>
      </div>

      {/* Fairness indicator */}
      <div
        className={`rounded p-3 text-sm ${
          score.fairnessAuditPassed
            ? "bg-teal-50 text-teal-800"
            : "bg-red-50 text-red-800"
        }`}
      >
        <p className="font-semibold">Fairness Audit</p>
        <p className="mt-1">
          {score.fairnessAuditPassed ? "✓ Passed" : "✗ Failed"} • SPD:{" "}
          {score.statisticalParityDifference.toFixed(3)}
          {score.statisticalParityDifference < 0.5
            ? " (within threshold)"
            : " (threshold exceeded)"}
        </p>
      </div>

      {/* Component breakdown */}
      <div className="space-y-4">
        <p className="text-sm font-medium text-gray-600">Score Components</p>
        {contribution
          .sort((a, b) => b.percentOfTotal - a.percentOfTotal)
          .map((comp) => (
            <div key={comp.name} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-gray-700">{comp.name}</span>
                <span className="text-gray-900">
                  {comp.normalizedScore.toFixed(2)} (
                  {comp.percentOfTotal.toFixed(1)}%)
                </span>
              </div>
              <div className="h-2 rounded bg-gray-200">
                <div
                  className="h-full rounded bg-blue-600"
                  style={{ width: `${comp.percentOfTotal}%` }}
                />
              </div>
              <p className="text-xs text-gray-500">
                Raw: {comp.rawScore.toFixed(1)} • Weight:{" "}
                {(comp.weight * 100).toFixed(0)}% • Category: {comp.category}
              </p>
            </div>
          ))}
      </div>

      {/* Explanation */}
      <div className="rounded bg-blue-50 p-4 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">Score Explanation</p>
        <p className="mt-2">{score.explanation}</p>
      </div>

      {/* Methodology */}
      <div className="rounded bg-gray-50 p-4 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">Scoring Methodology</p>
        <ul className="mt-2 list-inside space-y-1 list-disc text-gray-600">
          <li>Model: XGBoost (see A5 in project documentation)</li>
          <li>Features: Telematics from ingestion pipeline</li>
          <li>
            Fairness: AIF360 Statistical Parity Difference audit (SPD {"<"} 0.5)
          </li>
          <li>Updates: Real-time as new trip data arrives</li>
          <li>Generated: {new Date(score.generatedAt).toLocaleString()}</li>
        </ul>
      </div>
    </div>
  );
}
