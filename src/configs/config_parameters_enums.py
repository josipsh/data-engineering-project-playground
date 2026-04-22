from enum import Enum

class ConfigParameters(Enum):
    OUTPUT_FORMAT = "output-format"
    OUTPUT_TYPE = "output-type"
    NUMBER_OF_DEVICES_PER_FLEET = "number-of-devices-per-fleet"
    NUMBER_OF_FLEETS = "number-of-fleets"
    RATE_OF_EMITTING_DP = "rate-of-emitting-dp"
    ERROR_RATE = "error-rate"
    DIMENSIONS = "dimensions"

class Components(Enum):
    SENSORS = "sensors"
    COMPUTER = "computer"
    BATTERY = "battery"
    SOLAR_PANEL = "solar-panel"
