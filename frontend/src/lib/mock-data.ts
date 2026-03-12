/**
 * Mock data layer for POC.
 * RUBRIC: Clean Architecture—separates mock data from API logic.
 * In production, this would be replaced with real PostgreSQL queries.
 */

import type {
  TripScore,
  DriverBehaviorProfile,
  DriverAppeal,
} from '@/lib/types/scoring';
import type { SHAPOutput, LIMEOutput, FairnessAudit } from '@/lib/types/explainability';

// Mock tenant isolation
const MOCK_TENANT_ID = 'tenant_demo_001';
const MOCK_DRIVER_ID_1 = 'driver_alice_001';
const MOCK_DRIVER_ID_2 = 'driver_bob_002';

export const mockDrivers = [
  {
    id: MOCK_DRIVER_ID_1,
    tenantId: MOCK_TENANT_ID,
    name: 'Alice Johnson',
    email: 'alice@fleet.example.com',
    totalTrips: 142,
    averageScore: 82.5,
    status: 'active' as const,
  },
  {
    id: MOCK_DRIVER_ID_2,
    tenantId: MOCK_TENANT_ID,
    name: 'Bob Smith',
    email: 'bob@fleet.example.com',
    totalTrips: 98,
    averageScore: 71.2,
    status: 'active' as const,
  },
];

export const mockTrips = [
  {
    tripId: 'trip_20250310_001',
    driverId: MOCK_DRIVER_ID_1,
    tenantId: MOCK_TENANT_ID,
    startTime: '2025-03-10T08:00:00Z',
    endTime: '2025-03-10T16:30:00Z',
    distance: 320,
    score: 85,
    status: 'completed' as const,
  },
  {
    tripId: 'trip_20250310_002',
    driverId: MOCK_DRIVER_ID_2,
    tenantId: MOCK_TENANT_ID,
    startTime: '2025-03-10T09:00:00Z',
    endTime: '2025-03-10T17:00:00Z',
    distance: 280,
    score: 68,
    status: 'completed' as const,
  },
];

export const mockTripScores: Record<string, TripScore> = {
  trip_20250310_001: {
    tripId: 'trip_20250310_001',
    driverId: MOCK_DRIVER_ID_1,
    tenantId: MOCK_TENANT_ID,
    totalScore: 85,
    scoreBreakdown: [
      {
        name: 'Acceleration Control',
        category: 'acceleration',
        rawScore: 92,
        normalizedScore: 0.92,
        weight: 0.2,
        contribution: 18.4,
      },
      {
        name: 'Braking Safety',
        category: 'braking',
        rawScore: 88,
        normalizedScore: 0.88,
        weight: 0.25,
        contribution: 22,
      },
      {
        name: 'Speed Compliance',
        category: 'speed',
        rawScore: 82,
        normalizedScore: 0.82,
        weight: 0.3,
        contribution: 24.6,
      },
      {
        name: 'Cornering Smoothness',
        category: 'cornering',
        rawScore: 79,
        normalizedScore: 0.79,
        weight: 0.25,
        contribution: 19.75,
      },
    ],
    riskLevel: 'low',
    fairnessAuditPassed: true,
    statisticalParityDifference: 0.18,
    explanation:
      'Trip score of 85 indicates good driving behavior with strong acceleration and braking control. Minimal harsh events detected.',
    generatedAt: '2025-03-10T16:35:00Z',
  },
  trip_20250310_002: {
    tripId: 'trip_20250310_002',
    driverId: MOCK_DRIVER_ID_2,
    tenantId: MOCK_TENANT_ID,
    totalScore: 68,
    scoreBreakdown: [
      {
        name: 'Acceleration Control',
        category: 'acceleration',
        rawScore: 65,
        normalizedScore: 0.65,
        weight: 0.2,
        contribution: 13,
      },
      {
        name: 'Braking Safety',
        category: 'braking',
        rawScore: 72,
        normalizedScore: 0.72,
        weight: 0.25,
        contribution: 18,
      },
      {
        name: 'Speed Compliance',
        category: 'speed',
        rawScore: 68,
        normalizedScore: 0.68,
        weight: 0.3,
        contribution: 20.4,
      },
      {
        name: 'Cornering Smoothness',
        category: 'cornering',
        rawScore: 65,
        normalizedScore: 0.65,
        weight: 0.25,
        contribution: 16.25,
      },
    ],
    riskLevel: 'medium',
    fairnessAuditPassed: true,
    statisticalParityDifference: 0.22,
    explanation:
      'Trip score of 68 indicates moderate driving behavior. Multiple harsh braking events detected. Consider coaching on anticipatory braking.',
    generatedAt: '2025-03-10T17:05:00Z',
  },
};

export const mockSHAPData: Record<string, SHAPOutput> = {
  trip_20250310_001: {
    baseValue: 50,
    shapeValues: [
      {
        featureName: 'Harsh braking events',
        featureValue: 2,
        contribution: 5,
        magnitude: 5,
        direction: 'positive',
        percentileRank: 85,
      },
      {
        featureName: 'Speed violations',
        featureValue: 0,
        contribution: 12,
        magnitude: 12,
        direction: 'positive',
        percentileRank: 92,
      },
      {
        featureName: 'Cornering smoothness',
        featureValue: 0.91,
        contribution: 8,
        magnitude: 8,
        direction: 'positive',
        percentileRank: 78,
      },
      {
        featureName: 'Trip duration (hours)',
        featureValue: 8.5,
        contribution: -3,
        magnitude: 3,
        direction: 'negative',
        percentileRank: 25,
      },
    ],
    predictionValue: 82,
    modelName: 'Driver Behavior XGBoost',
    instanceId: 'trip_20250310_001',
    timestamp: '2025-03-10T16:35:00Z',
  },
};

export const mockLIMEData: Record<string, LIMEOutput> = {
  trip_20250310_001: {
    prediction: 'safe_driving',
    confidence: 0.87,
    explanation:
      'This trip is classified as safe driving due to minimal harsh events and good speed compliance.',
    weights: [
      { featureName: 'Speed violations', weight: 0.35, direction: 'supports' },
      {
        featureName: 'Harsh braking events',
        weight: 0.28,
        direction: 'supports',
      },
      {
        featureName: 'Acceleration smoothness',
        weight: 0.22,
        direction: 'supports',
      },
      {
        featureName: 'Heavy traffic exposure',
        weight: -0.15,
        direction: 'opposes',
      },
    ],
    instanceIndex: 0,
    modelName: 'Behavior Classifier',
    timestamp: '2025-03-10T16:35:00Z',
  },
};

export const mockFairnessAudit: FairnessAudit = {
  auditId: 'audit_20250310_001',
  timestamp: '2025-03-10T17:00:00Z',
  globalStatisticalParityDifference: 0.18,
  cohortSpd: {
    novice_drivers: 0.25,
    experienced_drivers: -0.12,
    young_drivers: 0.31,
    senior_drivers: 0.05,
  },
  referenceGroup: 'experienced_drivers',
  underprivilegedGroup: 'novice_drivers',
  debiasMethod: 'reweighting',
  impactOnScoring: {
    avgScoreShift: 2.3,
    maxScoreShift: 8.5,
    minScoreShift: -1.2,
  },
};

export const mockDriverBehavior: Record<string, DriverBehaviorProfile> = {
  [MOCK_DRIVER_ID_1]: {
    driverId: MOCK_DRIVER_ID_1,
    tenantId: MOCK_TENANT_ID,
    totalTrips: 142,
    averageScore: 82.5,
    totalRiskIncidents: 8,
    burnoutRiskLevel: 0,
    burnoutIndicators: [],
    emotionalTrajectory: [
      {
        feedback: 'Great trip today, feeling good!',
        sentiment: 'positive',
        sentimentScore: 0.92,
        timestamp: '2025-03-09T17:00:00Z',
      },
      {
        feedback: 'Tired but made good time.',
        sentiment: 'neutral',
        sentimentScore: 0.55,
        timestamp: '2025-03-08T17:00:00Z',
      },
    ],
    coachingHistory: [
      {
        tripId: 'trip_20250308_001',
        generatedCoaching:
          'Excellent work today, Alice! Your smooth cornering demonstrates strong vehicle control.',
        tone: 'encouraging',
        driverAcknowledged: true,
        acknowledgedAt: '2025-03-08T18:00:00Z',
      },
    ],
    lastUpdated: '2025-03-10T16:35:00Z',
  },
  [MOCK_DRIVER_ID_2]: {
    driverId: MOCK_DRIVER_ID_2,
    tenantId: MOCK_TENANT_ID,
    totalTrips: 98,
    averageScore: 71.2,
    totalRiskIncidents: 24,
    burnoutRiskLevel: 1,
    burnoutIndicators: [
      'Declining feedback sentiment',
      'Increased harsh braking events',
      'Multiple speed violations',
    ],
    emotionalTrajectory: [
      {
        feedback: 'Exhausted, traffic was brutal',
        sentiment: 'negative',
        sentimentScore: 0.18,
        timestamp: '2025-03-09T17:00:00Z',
      },
      {
        feedback: 'Not feeling it today',
        sentiment: 'negative',
        sentimentScore: 0.25,
        timestamp: '2025-03-08T17:00:00Z',
      },
    ],
    coachingHistory: [
      {
        tripId: 'trip_20250308_002',
        generatedCoaching:
          'Bob, we noticed some harsh braking in today\'s trip. Let\'s focus on anticipating traffic flow to smooth out your stops. You\'ve got this!',
        tone: 'supportive',
        driverAcknowledged: false,
      },
    ],
    lastUpdated: '2025-03-10T17:05:00Z',
  },
};

export const mockAppeals: DriverAppeal[] = [
  {
    appealId: 'appeal_001',
    driverId: MOCK_DRIVER_ID_2,
    tripId: 'trip_20250309_001',
    tenantId: MOCK_TENANT_ID,
    appeal:
      'I believe this score is unfair. I had to make emergency maneuvers due to another vehicle cutting me off.',
    status: 'under_review',
    aiDraftResponse:
      'We understand your concern. Context enrichment shows heavy traffic in the area. Let\'s review the video footage together.',
    fleetManagerReview:
      'Escalated for human review - video shows legitimate defensive driving.',
    fleetManagerDecision: 'partial',
    createdAt: '2025-03-09T18:00:00Z',
  },
];
