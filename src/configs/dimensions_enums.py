from enum import Enum


class SensorDimension(Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    OZONE = "ozone"
    NITROGEN_DIOXIDE = "nitrogen-dioxide"
    BAROMETRIC_PRESSURE = "barometric-pressure"
    SOLAR_RADIATION = "solar-radiation"
    SALINITY = "salinity"
    PH = "ph"
    PLASTICS = "plastics"

class ComputerDimension(Enum):
    CPU_TEMPERATURE = "cpu-temperature"
    CPU_UTILIZATION = "cpu-utilization"

class BatteryDimension(Enum):
    BATTERY_TEMPERATURE = "battery-temperature"
    BATTERY_PERCENTAGE_LEVEL = "battery-percentage-level"


class SolarPanelDimension(Enum):
    CURRENT_VOLTAGE = "current-voltage"
    CURRENT_AMP = "current-amp"
