from enum import StrEnum


class Priority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PingType(StrEnum):
    EMERGENCY = "emergency"
    HIGH_SPEED = "high_speed"
    MEDIUM_SPEED = "medium_speed"
    BATCH = "batch"
    START_OF_TRIP = "start_of_trip"
    END_OF_TRIP = "end_of_trip"


class Source(StrEnum):
    TELEMATICS_DEVICE = "telematics_device"
    DRIVER_APP = "driver_app"
    SYSTEM = "system"


class AgentName(StrEnum):
    ORCHESTRATOR = "orchestrator"
    SAFETY = "safety"
    SCORING = "scoring"
    DRIVER_SUPPORT = "driver_support"
    SENTIMENT = "sentiment"
