"use client";

import React from "react";
import { cn } from "@/lib/utils";
import type { LIMEOutput } from "@/lib/types/explainability";

interface LIMEExplanationProps {
  data: LIMEOutput;
  className?: string;
}

/**
 * LIMEExplanation shows local interpretable model-agnostic explanations.
 * RUBRIC: XRAI—human-friendly per-instance explanations.
 * Reference: A5 (XGBoost Fairness & Explainability)
 */
export function LIMEExplanation({ data, className }: LIMEExplanationProps) {
  return (
    <div
      className={cn(
        "space-y-4 rounded-lg border border-gray-200 bg-white p-6",
        className,
      )}
    >
      <div>
        <h3 className="font-semibold text-gray-900">
          LIME Explanation (Instance #{data.instanceIndex})
        </h3>
        <p className="mt-1 text-sm text-gray-600">
          Local Interpretable Model-Agnostic Explanation
        </p>
      </div>

      {/* Prediction badge */}
      <div className="rounded bg-gray-50 p-4">
        <p className="text-sm text-gray-600">Predicted Class</p>
        <div className="mt-1 flex items-center gap-3">
          <span className="text-xl font-bold text-gray-900">
            {data.prediction}
          </span>
          <div className="flex-1 h-2 rounded bg-gray-200 max-w-xs">
            <div
              className="h-full rounded bg-blue-600"
              style={{ width: `${data.confidence * 100}%` }}
            />
          </div>
          <span className="text-sm font-medium text-gray-700">
            {(data.confidence * 100).toFixed(1)}%
          </span>
        </div>
      </div>

      {/* Explanation text */}
      <div className="rounded bg-amber-50 p-3 text-sm text-amber-800">
        <p className="font-semibold">Explanation</p>
        <p className="mt-1">{data.explanation}</p>
      </div>

      {/* Feature importance */}
      <div className="space-y-3">
        <p className="text-sm font-medium text-gray-600">Feature Importance</p>
        {data.weights
          .sort((a, b) => Math.abs(b.weight) - Math.abs(a.weight))
          .map((w, idx) => (
            <div key={idx} className="flex items-center gap-3">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-700">
                  {w.featureName}
                </p>
                <p className="text-xs text-gray-500">
                  {w.direction === "supports"
                    ? "Supports prediction"
                    : "Opposes prediction"}
                </p>
                {w.featureValue !== undefined && (
                  <p className="text-xs text-gray-400 font-mono">
                    Value:{" "}
                    {typeof w.featureValue === "number"
                      ? w.featureValue.toFixed(2)
                      : w.featureValue}
                  </p>
                )}
              </div>
              <div className="h-2 w-24 rounded bg-gray-200">
                <div
                  className={`h-full rounded ${
                    w.direction === "supports" ? "bg-teal-500" : "bg-red-500"
                  }`}
                  style={{ width: `${Math.abs(w.weight) * 100}%` }}
                />
              </div>
              <span className="w-16 text-right text-sm font-semibold text-gray-700">
                {w.weight.toFixed(3)}
              </span>
            </div>
          ))}
      </div>

      {/* Fairness context */}
      <div className="rounded bg-blue-50 p-3 text-sm text-gray-700">
        <p className="font-semibold text-gray-900">Fairness Context</p>
        <p className="mt-1">
          Generated with AIF360 bias audits. See project documentation for
          Statistical Parity Difference metrics.
        </p>
      </div>
    </div>
  );
}
