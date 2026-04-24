from dataclasses import dataclass

from src.configs.config_parameters_enums import Components, ConfigParameters
from src.configs.dimensions_enums import BatteryDimension, ComputerDimension, SensorDimension, SolarPanelDimension
from src.configs.output_enums import OutputFormat, OutputType
from src.configs.rate_enums import EmitRate, ErrorRate
from src.errors.config_error import ConfigError


def _get_all_valid_dimensions() -> list[str]:
    all_dimensions: list = []
    all_dimensions.extend(SensorDimension)
    all_dimensions.extend(BatteryDimension)
    all_dimensions.extend(SolarPanelDimension)
    all_dimensions.extend(ComputerDimension)
    all_dimensions_str = [x.value for x in all_dimensions]
    return all_dimensions_str

ALL_VALID_DIMENSIONS = _get_all_valid_dimensions()

@dataclass()
class DimensionValue:
    is_enabled: bool
    error_rate: ErrorRate

    def to_dict(self) -> dict:
        return {"is_enabled":self.is_enabled, "error_rate": self.error_rate.name}


@dataclass()
class SensorDimensions:
    temperature: DimensionValue
    humidity: DimensionValue
    co2: DimensionValue
    ozone: DimensionValue
    nitrogen_dioxide: DimensionValue
    barometric_pressure: DimensionValue
    solar_radiation: DimensionValue
    salinity: DimensionValue
    ph: DimensionValue
    plastics: DimensionValue


    def to_dict(self) -> dict:
        return {
            "temperature": self.temperature.to_dict(),
            "humidity": self.humidity.to_dict(),
            "co2": self.co2.to_dict(),
            "ozone": self.ozone.to_dict(),
            "nitrogen_dioxide": self.nitrogen_dioxide.to_dict(),
            "barometric_pressure": self.barometric_pressure.to_dict(),
            "solar_radiation": self.solar_radiation.to_dict(),
            "salinity": self.salinity.to_dict(),
            "ph": self.ph.to_dict(),
            "plastics": self.plastics.to_dict()
        }
    

    @staticmethod
    def from_dict(
        dimension_data: list[SensorDimension],
        error_rate: dict[str, float]
    ) -> "SensorDimensions":
        return SensorDimensions(
            temperature=DimensionValue(
                is_enabled=SensorDimension.TEMPERATURE in dimension_data,
                error_rate=error_rate.get(SensorDimension.TEMPERATURE, ErrorRate.NONE)
            ),
            humidity=DimensionValue(
                is_enabled=SensorDimension.HUMIDITY in dimension_data,
                error_rate=error_rate.get(SensorDimension.HUMIDITY, ErrorRate.NONE)
            ),
            co2=DimensionValue(
                is_enabled=SensorDimension.CO2 in dimension_data,
                error_rate=error_rate.get(SensorDimension.CO2, ErrorRate.NONE)
            ),
            ozone=DimensionValue(
                is_enabled=SensorDimension.OZONE in dimension_data,
                error_rate=error_rate.get(SensorDimension.OZONE, ErrorRate.NONE)
            ),
            nitrogen_dioxide=DimensionValue(
                is_enabled=SensorDimension.NITROGEN_DIOXIDE in dimension_data,
                error_rate=error_rate.get(SensorDimension.NITROGEN_DIOXIDE, ErrorRate.NONE)
            ),
            barometric_pressure=DimensionValue(
                is_enabled=SensorDimension.BAROMETRIC_PRESSURE in dimension_data,
                error_rate=error_rate.get(SensorDimension.BAROMETRIC_PRESSURE, ErrorRate.NONE)
            ),
            solar_radiation=DimensionValue(
                is_enabled=SensorDimension.SOLAR_RADIATION in dimension_data,
                error_rate=error_rate.get(SensorDimension.SOLAR_RADIATION, ErrorRate.NONE)
            ),
            salinity=DimensionValue(
                is_enabled=SensorDimension.SALINITY in dimension_data,
                error_rate=error_rate.get(SensorDimension.SALINITY, ErrorRate.NONE)
            ),
            ph=DimensionValue(
                is_enabled=SensorDimension.PH in dimension_data,
                error_rate=error_rate.get(SensorDimension.PH, ErrorRate.NONE)
            ),
            plastics=DimensionValue(
                is_enabled=SensorDimension.PLASTICS in dimension_data,
                error_rate=error_rate.get(SensorDimension.PLASTICS, ErrorRate.NONE)
            ),
        )

@dataclass()
class ComputerDimensions:
    cpu_temperature: DimensionValue
    cpu_utilization: DimensionValue

    def to_dict(self) -> dict:
        return {
            "cpu_temperature": self.cpu_temperature.to_dict(),
            "cpu_utilization": self.cpu_utilization.to_dict()
        }
    
    @staticmethod
    def from_dict(
        dimension_data: list[ComputerDimension], 
        error_rate: dict[str, float]
    ) -> "ComputerDimensions":
        return ComputerDimensions(
            cpu_temperature=DimensionValue(
                is_enabled=ComputerDimension.CPU_TEMPERATURE in dimension_data,
                error_rate=error_rate.get(ComputerDimension.CPU_TEMPERATURE, ErrorRate.NONE)
            ),
            cpu_utilization=DimensionValue(
                is_enabled=ComputerDimension.CPU_UTILIZATION in dimension_data,
                error_rate=error_rate.get(ComputerDimension.CPU_UTILIZATION, ErrorRate.NONE)
            ),
        )

@dataclass()
class BatteryDimensions:
    battery_temperature: DimensionValue
    battery_percentage_level: DimensionValue

    def to_dict(self) -> dict:
        return {
            "battery_temperature": self.battery_temperature.to_dict(),
            "battery_percentage_level": self.battery_percentage_level.to_dict()
        }
    
    @staticmethod
    def from_dict(
        dimension_data: list[BatteryDimension], 
        error_rate: dict[str, float]
    ) -> "BatteryDimensions":
        return BatteryDimensions(
            battery_temperature=DimensionValue(
                is_enabled=BatteryDimension.BATTERY_TEMPERATURE in dimension_data,
                error_rate=error_rate.get(BatteryDimension.BATTERY_TEMPERATURE, ErrorRate.NONE)
            ),
            battery_percentage_level=DimensionValue(
                is_enabled=BatteryDimension.BATTERY_PERCENTAGE_LEVEL in dimension_data,
                error_rate=error_rate.get(BatteryDimension.BATTERY_PERCENTAGE_LEVEL, ErrorRate.NONE)
            ),
        )

@dataclass()
class SolarPanelDimensions:
    current_voltage: DimensionValue
    current_amp: DimensionValue

    def to_dict(self) -> dict:
        return {
            "current_voltage": self.current_voltage.to_dict(),
            "current_amp": self.current_amp.to_dict()
        }
    
    @staticmethod
    def from_dict(
        dimension_data: list[SolarPanelDimension], 
        error_rate: dict[str, float]
    ) -> "SolarPanelDimensions":
        return SolarPanelDimensions(
            current_voltage=DimensionValue(
                is_enabled=SolarPanelDimension.CURRENT_VOLTAGE in dimension_data,
                error_rate=error_rate.get(SolarPanelDimension.CURRENT_VOLTAGE, ErrorRate.NONE)
            ),
            current_amp=DimensionValue(
                is_enabled=SolarPanelDimension.CURRENT_AMP in dimension_data,
                error_rate=error_rate.get(SolarPanelDimension.CURRENT_AMP, ErrorRate.NONE)
            ),
        )


@dataclass()
class Dimensions:
    sensors: SensorDimensions
    computer: ComputerDimensions
    battery: BatteryDimensions
    solar_panel: SolarPanelDimensions

    def to_dict(self) -> dict:
        return {
            "sensors":self.sensors.to_dict(),
            "computer": self.computer.to_dict(),
            "battery": self.battery.to_dict(),
            "solar_panel": self.solar_panel.to_dict(),
        }


@dataclass()
class Config:
    output_format: OutputFormat
    output_type: OutputType
    number_of_devices_per_fleet: int
    number_of_fleets: int
    dimensions: Dimensions
    rate_of_emitting_dp: EmitRate

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        if not isinstance(data, dict):
            raise ConfigError(f"config must be a dict, got {type(data).__name__}")

        errors: list[str] = []

        output_format = _parse_enum(data, ConfigParameters.OUTPUT_FORMAT, OutputFormat, errors)
        output_type = _parse_enum(data, ConfigParameters.OUTPUT_TYPE, OutputType, errors)
        number_of_devices_per_fleet = _parse_positive_int(data, ConfigParameters.NUMBER_OF_DEVICES_PER_FLEET, errors)
        number_of_fleets = _parse_positive_int(data, ConfigParameters.NUMBER_OF_FLEETS, errors)
        rate_of_emitting_dp = _parse_enum(data, ConfigParameters.RATE_OF_EMITTING_DP, EmitRate, errors)
        dimensions = _parse_dimensions(data, errors)
        _check_if_unsupported_parameter_is_provided(data, errors)

        if errors:
            errors_str = "\n".join(errors)
            error_msg = f"While processing configuration the following errors occurred:\n{errors_str}"
            raise ConfigError(error_msg)

        return cls(
            output_format=output_format,
            output_type=output_type,
            number_of_devices_per_fleet=number_of_devices_per_fleet,
            number_of_fleets=number_of_fleets,
            dimensions=dimensions,
            rate_of_emitting_dp=rate_of_emitting_dp,
        )

    def to_dict(self) -> dict:
        return {
            "output-format": self.output_format.value,
            "output-type": self.output_type.value,
            "number-of-devices-per-fleet": self.number_of_devices_per_fleet,
            "number-of-fleets": self.number_of_fleets,
            "rate-of-emitting-dp": self.rate_of_emitting_dp.value,
            "dimensions": self.dimensions.to_dict()
        }


def _parse_enum(data: dict, key: ConfigParameters, enum_cls: type, errors: list[str]) -> object | None:
    value = data.get(key.value)
    if value is None:
        errors.append(f"- Missing required parameter: `{key.value}`")
        return None
    try:
        return enum_cls(value)
    except ValueError:
        valid = ", ".join(repr(m.value) for m in enum_cls)
        errors.append(f"- Invalid value for `{key.value}`: {value!r}. Expected one of: {valid}")
        return None

def _parse_positive_int(data: dict, key: ConfigParameters, errors: list[str]) -> int | None:
    value = data.get(key.value)
    if value is None:
        errors.append(f"- Missing required parameter: `{key.value}`")
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        errors.append(f"- Invalid value for `{key.value}`: {value!r}. Expected a positive integer.")
        return None
    return value

def _check_if_unsupported_parameter_is_provided(data: dict, errors: list[str]):
    valid_parameters = [x.value for x in ConfigParameters]
    unsupported_parameters = [k for k in data if k not in valid_parameters]
    if len(unsupported_parameters) > 0:
        unsupported_parameters_str = ', '.join(unsupported_parameters)
        errors.append((
            "- Unsupported parameter was found, make sure there is no typos. "
            f"Unsupported parameters: {unsupported_parameters_str}"
        ))

def _parse_dimensions(data: dict, errors: list[str]) -> Dimensions | None:
    dimensions_data = data.get(ConfigParameters.DIMENSIONS.value)
    error_rate_data = data.get(ConfigParameters.ERROR_RATE.value, {})
    
    if dimensions_data is None:
        errors.append(f"- Missing required parameter: `{ConfigParameters.DIMENSIONS.value}`")
        return None
    
    error_rate_data, error_rate_errors = _get_valid_error_rates(error_rate_data)
    valid_dimensions, dimension_error = _get_valid_dimensions(dimensions_data)
    if dimension_error is not None and error_rate_errors is None:
        errors.append(dimension_error)
        return None
    elif dimension_error is None and error_rate_errors is not None:
        errors.append(error_rate_errors)
        return None

    sensors_dimensions: list[SensorDimension] = [x for x in SensorDimension if x.value in valid_dimensions]
    computer_dimensions: list[ComputerDimension] = [x for x in ComputerDimension if x.value in valid_dimensions]
    battery_dimensions: list[BatteryDimension] = [x for x in BatteryDimension if x.value in valid_dimensions]
    solar_panel_dimensions: list[SolarPanelDimension] = [x for x in SolarPanelDimension if x.value in valid_dimensions]

    sensor_error_rates = error_rate_data.get(Components.SENSORS, {})
    computer_error_rates = error_rate_data.get(Components.COMPUTER, {})
    battery_error_rates = error_rate_data.get(Components.BATTERY, {})
    solar_panel_error_rates = error_rate_data.get(Components.SOLAR_PANEL, {})

    return Dimensions(
        sensors=SensorDimensions.from_dict(sensors_dimensions, sensor_error_rates),
        computer=ComputerDimensions.from_dict(computer_dimensions, computer_error_rates),
        battery=BatteryDimensions.from_dict(battery_dimensions, battery_error_rates),
        solar_panel=SolarPanelDimensions.from_dict(solar_panel_dimensions, solar_panel_error_rates)
    )

def _get_valid_dimensions(dimensions_data: list[str]) -> tuple[list[str] | None, str | None]:
    valid_dimensions = ', '.join(ALL_VALID_DIMENSIONS)
    if isinstance(dimensions_data, list) and len(dimensions_data) == 0:
        return(None, (
            f"- Invalid value for `{ConfigParameters.DIMENSIONS.value}` parameter.\n"
            f"Received value is an empty list.\n"
            f"Expected 'all' or a non-empty list of dimension strings. The valid dimensions are `{valid_dimensions}`"
        ))

    elif isinstance(dimensions_data, str) and dimensions_data != 'all':
        return(None, (
            f"- Invalid value for 'dimensions': {dimensions_data!r}. "
            f"Expected 'all' or a non-empty list of dimension strings the valid dimensions are `{valid_dimensions}`"
        ))

    elif isinstance(dimensions_data, str) and dimensions_data == 'all':
        return (ALL_VALID_DIMENSIONS, None)

    elif isinstance(dimensions_data, list) and len(dimensions_data) > 0:
        invalid_dimensions = [x for x in dimensions_data if x not in ALL_VALID_DIMENSIONS]
        if len(invalid_dimensions) > 0:
            invalid_dimensions_str = ', '.join(invalid_dimensions)
            return(None, (
                f"- Invalid value for `{ConfigParameters.DIMENSIONS.value}` parameter.\n"
                f"Invalid dimensions are: {invalid_dimensions_str}\n"
                f"Expected 'all' or a non-empty list of dimension strings. The valid dimensions are `{valid_dimensions}`"
            ))

        return (dimensions_data, None)

    return (None, (
        "- Unexpected error accrued, this should not happen!."
        "If this occurred, please create an issue in the "
        "https://github.com/josipsh/data-engineering-project-playground/issues"
    ))


def _get_valid_error_rates(error_rates: dict) -> tuple[dict|None, str|None]:
    valid_components = [x.value for x in Components]

    if not isinstance(error_rates, dict):
        return (None, (

            f"- Invalid value for `error-rate`: we have got `{error_rates}`. "
            'An expected value is dict with components and dimensions, e.g. {"sensors": "temperature": 0.1}'
        ))
    local_errors = []
    data = {}
    for component, dimensions in error_rates.items():
        if component not in valid_components:
            valid_components_str = ', '.join(valid_components)
            local_errors.append(
                f"- Unknown component `{component}` occurred in `error-rate` parameter. "
                f"Valid components are: {valid_components_str}"
            )
            continue
        if not isinstance(dimensions, dict):
            local_errors.append(
                f"- Invalid value component {component}. We expect a `dict`, but we got `{type(dimensions).__name__}`. "
                'An expected value is dict with components and dimensions, e.g. {"sensors": "temperature": 0.1}'
            )
            continue

        comp = Components(component)
        data[comp] = {}
        for dimension, rate in dimensions.items():
            dimension_enum, error_rate, error = _get_valid_error_rate_data(comp, dimension, rate)
            if error is not None:
                local_errors.append(error)

            data[comp][dimension_enum] = error_rate

    if len(local_errors) >0:
        return (None, "\n".join(local_errors))
   
    return (data, None)

def _get_valid_error_rate_data(
    component: Components,
    dimension: str,
    rate: str | int | float
) -> tuple[SensorDimension | ComputerDimension | BatteryDimension | SolarPanelDimension | None, ErrorRate| None, str | None]:
    error_format = (
        "- Dimension in the component `{comp}` is invalid. Received dimension is `{dim}`. "
        "Valid dimensions for component `{comp}` are `{valid_dime}`"
    )
    sensors_valid_dimensions = [x.value for x in SensorDimension]
    computer_valid_dimensions = [x.value for x in ComputerDimension]
    battery_valid_dimensions = [x.value for x in BatteryDimension]
    solar_panel_valid_dimensions = [x.value for x in SolarPanelDimension]


    if component == Components.SENSORS and dimension not in sensors_valid_dimensions:
        valid_dim = ', '.join(sensors_valid_dimensions)
        return (None, None, error_format.format(comp=component.value, dim=dimension, valid_dime=valid_dim))
    elif component == Components.COMPUTER and dimension not in computer_valid_dimensions:
        valid_dim = ', '.join(computer_valid_dimensions)
        return (None, None, error_format.format(comp=component.value, dim=dimension, valid_dime=valid_dim))
    elif component == Components.BATTERY and dimension not in battery_valid_dimensions:
        valid_dim = ', '.join(battery_valid_dimensions)
        return (None, None, error_format.format(comp=component.value, dim=dimension, valid_dime=valid_dim))
    elif component == Components.SOLAR_PANEL and dimension not in solar_panel_valid_dimensions:
        valid_dim = ', '.join(solar_panel_valid_dimensions)
        return (None, None, error_format.format(comp=component.value, dim=dimension, valid_dime=valid_dim))

    valid_rates: list[float] = [x.value for x in ErrorRate]
    rate_float, error = try_converting_to_float(rate)
    if error is not None or rate_float not in valid_rates:
        valid_rates_str = ', '.join(str(r) for r in valid_rates)
        return (None, None, (
            f"- A value `{rate_float}` for the dimension `{dimension}` in the component `{component.value}` is invalid. "
            f"Valid values are: {valid_rates_str}"
        ))

    if component == Components.SENSORS:
        return (SensorDimension(dimension), ErrorRate(rate_float), None)
    elif component == Components.COMPUTER:
        return (ComputerDimension(dimension), ErrorRate(rate_float), None)
    elif component == Components.BATTERY:
        return (BatteryDimension(dimension), ErrorRate(rate_float), None)
    elif component == Components.SOLAR_PANEL:
        return (SolarPanelDimension(dimension), ErrorRate(rate_float), None)
    

    return (None, None, "- If you get this error, please create an issue in the github project!")

def try_converting_to_float(val: str | int | float) -> tuple[float | None, str | None]:
    if isinstance(val, float):
        return val, None
    
    try:
        return float(val), None
    except ValueError:
        return None, "It is not possible to convert to float"
