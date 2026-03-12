/**
 * Safety and real-time telemetry types.
 * RUBRIC: Performance—WebSocket schema for real-time < 500ms alerts.
 * Reference: A0 (4-Ping Telematics Lifecycle), A14 (Safety Intervention)
 */

export interface Telematics {
  eventId: string;
  deviceEventId: string;
  tripId: string;
  driverId: string;
  truckId: string;
  tenantId: string;
  eventType: TelemetryEventType;
  category: TelemetryCategory;
  priority: Priority;
  timestamp: ISO8601String;
  offsetSeconds?: number;
  location: {
    lat: number;
    lon: number;
  };
  media?: {
    videoUrl?: string;
    imageUrl?: string;
  };
  schemaVersion: string;
  details: Record<string, unknown>;
}

export type TelemetryEventType =
  | 'collision'
  | 'rollover'
  | 'harsh_brake'
  | 'hard_accel'
  | 'harsh_corner'
  | 'speeding'
  | 'excessive_idle'
  | 'vehicle_offline'
  | 'normal_operation'
  | 'start_of_trip'
  | 'end_of_trip'
  | 'driver_feedback';

export type TelemetryCategory =
  | 'critical'
  | 'harsh_event'
  | 'speed_compliance'
  | 'idle_fuel'
  | 'driver_feedback'
  | 'normal_operation';

export type Priority = 'critical' | 'high' | 'medium' | 'low';

/**
 * Critical event bypass to Safety Agent (Kafka → WebSocket)
 */
export interface CriticalEvent {
  eventId: string;
  driverId: string;
  tripId: string;
  tenantId: string;
  eventType: 'collision' | 'rollover' | 'extreme_harsh_brake' | 'manual_sos';
  severity: 'critical' | 'severe';
  gForceMagnitude?: number;
  rollAngle?: number;
  location: {
    lat: number;
    lon: number;
  };
  videoUrl?: string;
  timestamp: ISO8601String;
  contextData?: Record<string, unknown>;
}

/**
 * Safety intervention workflow
 */
export interface SafetyIntervention {
  interventionId: string;
  eventId: string;
  driverId: string;
  tenantId: string;
  level: 1 | 2 | 3;
  levelName: 'app_notification' | 'formal_message' | 'fleet_manager_escalation';
  message: string;
  timestamp: ISO8601String;
  completed: boolean;
  completedAt?: ISO8601String;
}

export type ISO8601String = string;
