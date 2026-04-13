from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal


class OutputFormat(Enum):
    JSON = "json"
    JSON_WITH_BINARY_PAYLOAD = "json-with-binary-payload"
    XML = "xml"
    XML_WITH_BINARY_PAYLOAD = "xml-with-binary-payload"
    CSV = "csv"
    CSV_WITH_BINARY_PAYLOAD = "csv-with-binary-payload"
    AVRO = "avro"
    AVRO_WITH_BINARY_PAYLOAD = "avro_with_binary_payload"  # underscore — matches PRD exactly


class OutputType(Enum):
    KAFKA_ONLY = "kafka-only"
    RABBITMQ_ONLY = "rabbitmq-only"
    S3_ONLY = "s3-only"
    S3_WITH_KAFKA = "s3-with-kafka"
    S3_WITH_RABBITMQ = "s3-with-rabbitmq"


class SensorsDimensions(Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    CO2 = "co2"
    OZONE = "ozone"
    NITROGEN_DIOXIDE = "nitrogen_dioxide"
    BAROMETRIC_PRESSURE = "barometric_pressure"
    SOLAR_RADIATION = "solar_radiation"
    SALINITY = "salinity"
    PH = "ph"
    DISSOLVED_OXYGEN = "dissolved_oxygen"
    TURBIDITY = "turbidity"
    ELECTRICAL_CONDUCTIVITY = "electrical_conductivity"
    METALS = "metals"
    PLASTICS = "plastics"


class ComputerDimensions(Enum):
    CPU_TEMPERATURE = "cpu_temperature"
    CPU_UTILIZATION = "cpu_utilization"


class BatteryDimensions(Enum):
    BATTERY_TEMPERATURE = "battery_temperature"
    BATTERY_PERCENTAGE_LEVEL = "battery_percentage_level"


class SolarPanelDimensions(Enum):
    CURRENT_VOLTAGE = "current_voltage"
    CURRENT_AMP = "current_amp"


# Antenna has no dimensions — only a component-level error rate applies.


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


# Component → dimension enum class mapping (antenna excluded — no dimensions)
_COMPONENT_DIMENSIONS: dict[
    str,
    type[SensorsDimensions | ComputerDimensions | BatteryDimensions | SolarPanelDimensions],
] = {
    "sensors": SensorsDimensions,
    "computer": ComputerDimensions,
    "battery": BatteryDimensions,
    "solar_panel": SolarPanelDimensions,
}

# Flat lookup: dimension string → enum member (across all components)
_ALL_DIMENSIONS: dict[
    str, SensorsDimensions | ComputerDimensions | BatteryDimensions | SolarPanelDimensions
] = {}
for _cls in _COMPONENT_DIMENSIONS.values():
    for _member in _cls:
        _ALL_DIMENSIONS[_member.value] = _member


def _parse_enum(data: dict, key: str, enum_cls: type, errors: list[str]) -> object | None:
    if key not in data:
        errors.append(f"missing required parameter: {key!r}")
        return None
    raw = data[key]
    try:
        return enum_cls(raw)
    except ValueError:
        valid = ", ".join(repr(m.value) for m in enum_cls)
        errors.append(f"invalid value for {key!r}: {raw!r}. Expected one of: {valid}")
        return None


def _parse_positive_int(data: dict, key: str, errors: list[str]) -> int | None:
    if key not in data:
        errors.append(f"missing required parameter: {key!r}")
        return None
    raw = data[key]
    if not isinstance(raw, int) or isinstance(raw, bool) or raw <= 0:
        errors.append(f"invalid value for {key!r}: {raw!r}. Expected a positive integer")
        return None
    return raw


def _parse_dimensions(
    data: dict, key: str, errors: list[str]
) -> frozenset | Literal["all"] | None:
    if key not in data:
        errors.append(f"missing required parameter: {key!r}")
        return None
    raw = data[key]
    if raw == "all":
        return "all"
    if not isinstance(raw, list) or len(raw) == 0:
        errors.append(
            f"invalid value for {key!r}: {raw!r}. Expected 'all' or a non-empty list of dimension strings"
        )
        return None
    unknown = [item for item in raw if item not in _ALL_DIMENSIONS]
    if unknown:
        valid = ", ".join(sorted(_ALL_DIMENSIONS.keys()))
        errors.append(f"invalid dimension(s) in {key!r}: {unknown!r}. Valid values: {valid}")
        return None
    return frozenset(_ALL_DIMENSIONS[item] for item in raw)


def _parse_error_rate_value(raw: object, context: str, errors: list[str]) -> ErrorRate | None:
    valid_values = sorted(m.value for m in ErrorRate)
    if not isinstance(raw, (int, float)) or isinstance(raw, bool):
        errors.append(
            f"invalid error-rate value at {context!r}: {raw!r}. Expected one of: {valid_values}"
        )
        return None
    try:
        return ErrorRate(float(raw))
    except ValueError:
        errors.append(
            f"invalid error-rate value at {context!r}: {raw!r}. Expected one of: {valid_values}"
        )
        return None


def _parse_error_rate(
    data: dict, key: str, errors: list[str]
) -> dict[str, dict[str, ErrorRate] | ErrorRate] | None:
    if key not in data or data[key] is None:
        return None
    raw = data[key]
    if raw == "none":
        return None
    if not isinstance(raw, dict):
        errors.append(
            f"invalid value for {key!r}: expected a mapping of component → rates, got {raw!r}"
        )
        return None

    valid_components = set(_COMPONENT_DIMENSIONS.keys()) | {"antenna"}
    result: dict[str, dict[str, ErrorRate] | ErrorRate] = {}

    for component, value in raw.items():
        if component not in valid_components:
            errors.append(
                f"unknown component in {key!r}: {component!r}. Valid: {sorted(valid_components)}"
            )
            continue

        if component == "antenna":
            rate = _parse_error_rate_value(value, "error-rate.antenna", errors)
            if rate is not None:
                result["antenna"] = rate
        else:
            if not isinstance(value, dict):
                errors.append(
                    f"error-rate.{component} must be a mapping of dimension → rate, got {value!r}"
                )
                continue
            dim_cls = _COMPONENT_DIMENSIONS[component]
            valid_dims = {m.value for m in dim_cls}
            component_result: dict[str, ErrorRate] = {}
            for dim, rate_raw in value.items():
                if dim not in valid_dims:
                    errors.append(
                        f"unknown dimension in error-rate.{component}: {dim!r}. Valid: {sorted(valid_dims)}"
                    )
                    continue
                rate = _parse_error_rate_value(rate_raw, f"error-rate.{component}.{dim}", errors)
                if rate is not None:
                    component_result[dim] = rate
            if component_result:
                result[component] = component_result

    return result if result else None


@dataclass(frozen=True)
class Config:
    output_format: OutputFormat
    output_type: OutputType
    number_of_devices_per_fleet: int
    number_of_fleets: int
    dimensions: frozenset[
        SensorsDimensions | ComputerDimensions | BatteryDimensions | SolarPanelDimensions
    ] | Literal["all"]
    rate_of_emitting_dp: EmitRate
    error_rate: dict[str, dict[str, ErrorRate] | ErrorRate] | None

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        if not isinstance(data, dict):
            raise ValueError(f"config must be a YAML mapping, got {type(data).__name__}")

        errors: list[str] = []

        output_format = _parse_enum(data, "output-format", OutputFormat, errors)
        output_type = _parse_enum(data, "output-type", OutputType, errors)
        number_of_devices_per_fleet = _parse_positive_int(data, "number-of-devices-per-fleet", errors)
        number_of_fleets = _parse_positive_int(data, "number-of-fleets", errors)
        dimensions = _parse_dimensions(data, "dimensions", errors)
        rate_of_emitting_dp = _parse_enum(data, "rate-of-emitting-dp", EmitRate, errors)
        error_rate = _parse_error_rate(data, "error-rate", errors)

        if errors:
            raise ValueError("\n".join(errors))

        return cls(
            output_format=output_format,
            output_type=output_type,
            number_of_devices_per_fleet=number_of_devices_per_fleet,
            number_of_fleets=number_of_fleets,
            dimensions=dimensions,
            rate_of_emitting_dp=rate_of_emitting_dp,
            error_rate=error_rate,
        )

    def __str__(self) -> str:
        lines = [
            f"output-format: {self.output_format.value}",
            f"output-type: {self.output_type.value}",
            f"number-of-devices-per-fleet: {self.number_of_devices_per_fleet}",
            f"number-of-fleets: {self.number_of_fleets}",
        ]

        if self.dimensions == "all":
            lines.append("dimensions: all")
        else:
            sorted_dims = sorted(d.value for d in self.dimensions)
            lines.append(f"dimensions: {', '.join(sorted_dims)}")

        lines.append(f"rate-of-emitting-dp: {self.rate_of_emitting_dp.value}")

        if self.error_rate is None:
            lines.append("error-rate: none")
        else:
            parts = []
            for component, value in sorted(self.error_rate.items()):
                if isinstance(value, ErrorRate):
                    parts.append(f"{component}={value.name.lower()}")
                else:
                    for dim, rate in sorted(value.items()):
                        parts.append(f"{component}.{dim}={rate.name.lower()}")
            lines.append(f"error-rate: {', '.join(parts)}")

        return "\n".join(lines)
