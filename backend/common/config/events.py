from typing import Any, Dict

from ..models.enums import Priority


class EventConfig:
    def __init__(
        self, category: str, priority: Priority, ml_weight: float, action: str
    ):
        self.category = category
        self.priority = priority
        self.ml_weight = ml_weight
        self.action = action


# ── PRIORITY MAP (Redis ZSet scores) ──────────────────────
# Note: Lower score = higher priority (for zpopmin)
PRIORITY_MAP = {
    Priority.CRITICAL: 0,
    Priority.HIGH: 3,
    Priority.MEDIUM: 6,
    Priority.LOW: 9,
}

# ── EVENT MATRIX ──────────────────────────────────────────
EVENT_MATRIX: Dict[str, EventConfig] = {
    "collision": EventConfig(
        "critical", Priority.CRITICAL, 1.0, "Emergency Alert & 911"
    ),
    "rollover": EventConfig(
        "critical", Priority.CRITICAL, 1.0, "Emergency Alert & 911"
    ),
    "vehicle_offline": EventConfig("critical", Priority.HIGH, 0.3, "Fleet Alert"),
    "harsh_brake": EventConfig("harsh_events", Priority.HIGH, 0.7, "Coaching"),
    "hard_accel": EventConfig("harsh_events", Priority.HIGH, 0.7, "Coaching"),
    "harsh_corner": EventConfig("harsh_events", Priority.HIGH, 0.6, "Coaching"),
    "speeding": EventConfig("speed_compliance", Priority.MEDIUM, 0.5, "Regulatory"),
    "excessive_idle": EventConfig("idle_fuel", Priority.LOW, 0.2, "Coaching"),
    "smoothness_log": EventConfig(
        "normal_operation", Priority.LOW, -0.2, "Reward Bonus"
    ),
    "normal_operation": EventConfig(
        "normal_operation", Priority.LOW, 0.0, "Analytics"
    ),
    "start_of_trip": EventConfig("trip_lifecycle", Priority.LOW, 0.0, "Logging"),
    "end_of_trip": EventConfig("trip_lifecycle", Priority.LOW, 0.0, "Scoring"),
    "driver_sos": EventConfig(
        "critical", Priority.CRITICAL, 0.0, "Emergency Alert"
    ),
    "driver_dispute": EventConfig("driver_feedback", Priority.HIGH, 0.0, "HITL"),
    "driver_complaint": EventConfig(
        "driver_feedback", Priority.HIGH, 0.0, "Support"
    ),
    "driver_feedback": EventConfig(
        "driver_feedback", Priority.MEDIUM, 0.0, "Sentiment"
    ),
    "driver_comment": EventConfig("driver_feedback", Priority.LOW, 0.0, "Sentiment"),
    "malicious_injection": EventConfig("security_scan", Priority.MEDIUM, 0.0, "Reject & Log"),
}

# ── THRESHOLDS ────────────────────────────────────────────
THRESHOLDS = {
    "idle": {
        "acceptable_seconds": 120,
        "warning_seconds": 300,
        "excessive_seconds": 300,
    },
    "rpm": {
        "normal_max": 1800,
        "acceptable_max": 2500,
        "over_rev_threshold": 2500,
        "over_rev_duration_seconds": 5,
    },
    "acceleration": {
        "harsh_brake_g": -0.7,
        "harsh_accel_g": 0.75,
        "harsh_corner_g": 0.8,
    },
    "jerk": {
        "smooth_threshold": 0.05,
    },
}
