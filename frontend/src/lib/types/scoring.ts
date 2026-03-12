/**
 * Scoring and behavior analysis types.
 * RUBRIC: XRAI—detailed scoring breakdown for explainability.
 * Reference: A5 (Behavior Agent, XGBoost, AIF360)
 */

export interface TripScore {
  tripId: string;
  driverId: string;
  tenantId: string;
  totalScore: number;
  scoreBreakdown: ScoreComponent[];
  riskLevel: "low" | "medium" | "high" | "critical";
  fairnessAuditPassed: boolean;
  statisticalParityDifference: number;
  explanation: string;
  generatedAt: ISO8601String;
}

export interface ScoreComponent {
  name: string;
  category: "acceleration" | "braking" | "cornering" | "speed" | "other";
  rawScore: number;
  normalizedScore: number;
  weight: number;
  contribution: number;
}

export interface DriverBehaviorProfile {
  driverId: string;
  tenantId: string;
  totalTrips: number;
  averageScore: number;
  totalRiskIncidents: number;
  burnoutRiskLevel: 0 | 1; // 0=low, 1=high
  burnoutIndicators: string[];
  emotionalTrajectory: EmotionalDataPoint[];
  coachingHistory: CoachingRecord[];
  lastUpdated: ISO8601String;
}

export interface EmotionalDataPoint {
  feedback: string;
  sentiment: "positive" | "neutral" | "negative";
  sentimentScore: number;
  timestamp: ISO8601String;
}

export interface CoachingRecord {
  tripId: string;
  generatedCoaching: string;
  tone: "encouraging" | "supportive" | "directive";
  driverAcknowledged: boolean;
  acknowledgedAt?: ISO8601String;
}

export interface DriverAppeal {
  appealId: string;
  driverId: string;
  tripId: string;
  tenantId: string;
  appeal: string;
  status: "pending" | "under_review" | "resolved" | "escalated";
  aiDraftResponse: string;
  fleetManagerReview?: string;
  fleetManagerDecision?: "upheld" | "overturned" | "partial";
  createdAt: ISO8601String;
  resolvedAt?: ISO8601String;
}

export type ISO8601String = string;
