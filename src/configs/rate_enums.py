from enum import Enum


class EmitRate(Enum):
    ONE_PER_SECOND = "1-per-second"
    TEN_PER_SECOND = "10-per-second"
    ONE_PER_MINUTE = "1-per-minute"
    TEN_PER_MINUTE = "10-per-minute"
    ONE_PER_HOUR = "1-per-hour"
    TEN_PER_HOUR = "10-per-hour"


class ErrorRate(Enum):
    NONE = 0.0
    LOW = 0.1
    MEDIUM = 0.25
    HIGH = 0.5
    CRITICAL = 0.75
    CERTAIN = 1.0
