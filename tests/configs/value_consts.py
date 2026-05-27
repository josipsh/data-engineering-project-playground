from src.configs.dimensions_enums import BatteryDimension, ComputerDimension, SensorDimension, SolarPanelDimension
from src.configs.config_parameters_enums import ConfigParameters, Components
from src.configs.config import BatteryDimensions, ComputerDimensions, Config, DimensionValue, Dimensions, SensorDimensions, SolarPanelDimensions
from src.configs.output_enums import OutputFormat, OutputType
from src.configs.rate_enums import EmitRate, ErrorRate


REQUIRED_ONLY_CONFIG = {
    ConfigParameters.OUTPUT_FORMAT.value: OutputFormat.JSON.value,
    ConfigParameters.OUTPUT_TYPE.value: OutputType.KAFKA_ONLY.value,
    ConfigParameters.NUMBER_OF_DEVICES_PER_FLEET.value: 50,
    ConfigParameters.NUMBER_OF_FLEETS.value: 5,
    ConfigParameters.DIMENSIONS.value: "all",
    ConfigParameters.RATE_OF_EMITTING_DP.value: EmitRate.TEN_PER_SECOND.value,
}

REQUIRED_AND_OPTIONAL_CONFIG = {
    **REQUIRED_ONLY_CONFIG,
    ConfigParameters.ERROR_RATE.value: {
        Components.SENSORS.value: {SensorDimension.TEMPERATURE.value: 0.1},
        Components.COMPUTER.value: {ComputerDimension.CPU_UTILIZATION.value: 0.25},
        Components.BATTERY.value: {BatteryDimension.BATTERY_TEMPERATURE.value: 0.5},
        Components.SOLAR_PANEL.value: {SolarPanelDimension.CURRENT_VOLTAGE.value: 0.75},
    },
}

EXPECTED_REQUIRED_ONLY_CONFIG: Config = Config(
    output_format = OutputFormat.JSON,
    output_type = OutputType.KAFKA_ONLY,
    number_of_devices_per_fleet = 50,
    number_of_fleets = 5,
    rate_of_emitting_dp = EmitRate.TEN_PER_SECOND,
    dimensions = Dimensions(
        sensors=SensorDimensions(
            temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            humidity=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            co2=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            ozone=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            nitrogen_dioxide=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            barometric_pressure=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            solar_radiation=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            salinity=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            ph=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            plastics=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        computer=ComputerDimensions(
            cpu_utilization=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            cpu_temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        battery=BatteryDimensions(
            battery_percentage_level=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            battery_temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        solar_panel=SolarPanelDimensions(
            current_amp=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            current_voltage=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        )
    ),
)

EXPECTED_REQUIRED_AND_OPTIONAL_CONFIG: Config = Config(
    output_format = OutputFormat.JSON,
    output_type = OutputType.KAFKA_ONLY,
    number_of_devices_per_fleet = 50,
    number_of_fleets = 5,
    rate_of_emitting_dp = EmitRate.TEN_PER_SECOND,
    dimensions = Dimensions(
        sensors=SensorDimensions(
            temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.LOW),
            humidity=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            co2=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            ozone=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            nitrogen_dioxide=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            barometric_pressure=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            solar_radiation=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            salinity=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            ph=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
            plastics=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        computer=ComputerDimensions(
            cpu_utilization=DimensionValue(is_enabled=True, error_rate=ErrorRate.MEDIUM),
            cpu_temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        battery=BatteryDimensions(
            battery_temperature=DimensionValue(is_enabled=True, error_rate=ErrorRate.HIGH),
            battery_percentage_level=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        ),
        solar_panel=SolarPanelDimensions(
            current_voltage=DimensionValue(is_enabled=True, error_rate=ErrorRate.CRITICAL),
            current_amp=DimensionValue(is_enabled=True, error_rate=ErrorRate.NONE),
        )
    ),
)
