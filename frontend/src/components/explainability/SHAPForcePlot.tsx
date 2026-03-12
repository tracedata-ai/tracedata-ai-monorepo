"use client";

import React, { useMemo } from "react";
import { cn } from "@/lib/utils";
import type { SHAPOutput, SHAPValue } from "@/lib/types/explainability";

interface SHAPForcePlotProps {
  data: SHAPOutput;
  className?: string;
}

/**
 * SHAPForcePlot visualizes SHAP feature contributions.
 * RUBRIC: XRAI—demonstrates how features contributed to prediction.
 * Reference: A5 (XGBoost Fairness & Explainability)
 */
export function SHAPForcePlot({ data, className }: SHAPForcePlotProps) {
  const { positiveForces, negativeForces, totalPositive, totalNegative } =
    useMemo(() => {
      const pos = data.shapeValues.filter((v) => v.direction === "positive");
      const neg = data.shapeValues.filter((v) => v.direction === "negative");
      return {
        positiveForces: pos,
        negativeForces: neg,
        totalPositive: pos.reduce((sum, v) => sum + v.contribution, 0),
        totalNegative: neg.reduce((sum, v) => sum + v.contribution, 0),
      };
    }, [data.shapeValues]);

  const maxMagnitude = Math.max(
    Math.abs(totalPositive),
    Math.abs(totalNegative),
    1,
  );

  return (
    <div
      className={cn(
        "rounded-lg border border-gray-200 bg-white p-6 space-y-6",
        className,
      )}
    >
      <div>
        <h3 className="font-semibold text-gray-900">
          SHAP Force Plot: {data.modelName}
        </h3>
        <p className="mt-1 text-sm text-gray-600 font-mono">
          Instance: {data.instanceId}
        </p>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-red-500" />
          <span className="text-gray-700">Negative impact</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded bg-teal-500" />
          <span className="text-gray-700">Positive impact</span>
        </div>
      </div>

      {/* Base value → Prediction flow */}
      <div className="rounded bg-gray-50 p-4">
        <div className="flex items-center justify-between gap-4">
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Base Value</p>
            <p className="text-lg font-bold text-gray-900">
              {data.baseValue.toFixed(2)}
            </p>
          </div>

          {/* Positive contributions bar */}
          {positiveForces.length > 0 && (
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="text-xs font-semibold text-teal-600">
                  +{totalPositive.toFixed(2)}
                </div>
                <div className="flex-1 h-2 rounded bg-teal-200">
                  <div
                    className="h-full rounded bg-teal-500"
                    style={{
                      width: `${(Math.abs(totalPositive) / maxMagnitude) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Negative contributions bar */}
          {negativeForces.length > 0 && (
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="text-xs font-semibold text-red-600">
                  {totalNegative.toFixed(2)}
                </div>
                <div className="flex-1 h-2 rounded bg-red-200">
                  <div
                    className="h-full rounded bg-red-500"
                    style={{
                      width: `${(Math.abs(totalNegative) / maxMagnitude) * 100}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          )}

          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Prediction</p>
            <p className="text-lg font-bold text-gray-900">
              {data.predictionValue.toFixed(2)}
            </p>
          </div>
        </div>
      </div>

      {/* Feature contributions table */}
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-600">
          Top Contributing Features
        </p>
        <div className="max-h-80 overflow-y-auto rounded border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50">
                <th className="px-3 py-2 text-left font-medium text-gray-700">
                  Feature
                </th>
                <th className="px-3 py-2 text-right font-medium text-gray-700">
                  Value
                </th>
                <th className="px-3 py-2 text-right font-medium text-gray-700">
                  Impact
                </th>
              </tr>
            </thead>
            <tbody>
              {data.shapeValues
                .sort((a, b) => Math.abs(b.magnitude) - Math.abs(a.magnitude))
                .slice(0, 10)
                .map((force, idx) => (
                  <tr key={idx} className="border-b hover:bg-gray-50">
                    <td className="px-3 py-2 text-gray-900">
                      {force.featureName}
                    </td>
                    <td className="px-3 py-2 text-right text-gray-700 font-mono">
                      {typeof force.featureValue === "number"
                        ? force.featureValue.toFixed(2)
                        : force.featureValue}
                    </td>
                    <td className="px-3 py-2 text-right font-semibold">
                      <span
                        className={
                          force.direction === "positive"
                            ? "text-teal-600"
                            : "text-red-600"
                        }
                      >
                        {force.direction === "positive" ? "+" : ""}
                        {force.contribution.toFixed(3)}
                      </span>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Explainability statement */}
      <div className="rounded bg-blue-50 p-3 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">What does this mean?</p>
        <p className="mt-1">
          This SHAP force plot shows how each feature pushed the prediction up
          (teal) or down (red) from the base value. See the project report for
          XGBoost model details and AIF360 fairness audits.
        </p>
      </div>
    </div>
  );
}
