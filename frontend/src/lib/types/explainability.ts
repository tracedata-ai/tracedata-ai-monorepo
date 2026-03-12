/**
 * Explainability (XAI) output types for SHAP, LIME, and other interpretability methods.
 * RUBRIC: XRAI—structured outputs for model interpretability.
 * Reference: A5 (XGBoost Fairness & Explainability)
 */

export interface SHAPOutput {
  baseValue: number;
  shapeValues: SHAPValue[];
  predictionValue: number;
  modelName: string;
  instanceId: string;
  timestamp: ISO8601String;
}

export interface SHAPValue {
  featureName: string;
  featureValue: number | string;
  contribution: number;
  magnitude: number;
  direction: "positive" | "negative";
  percentileRank?: number;
}

export interface LIMEOutput {
  prediction: string;
  confidence: number;
  explanation: string;
  weights: LIMEWeight[];
  instanceIndex: number;
  modelName: string;
  timestamp: ISO8601String;
}

export interface LIMEWeight {
  featureName: string;
  weight: number;
  direction: "supports" | "opposes";
  featureValue?: string | number;
}

export interface FairnessAudit {
  auditId: string;
  timestamp: ISO8601String;
  globalStatisticalParityDifference: number;
  cohortSpd: Record<string, number>; // e.g., {"novice": 0.15, "experienced": -0.12}
  referenceGroup: string;
  underprivilegedGroup: string;
  debiasMethod: "reweighting" | "threshold" | "adversarial";
  impactOnScoring: {
    avgScoreShift: number;
    maxScoreShift: number;
    minScoreShift: number;
  };
}

export type ISO8601String = string;
