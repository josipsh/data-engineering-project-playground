import pytest
import copy

import tests.configs.value_consts as tests_config_val
from src.configs.config import Config
from src.configs.dimensions_enums import SensorDimension, ComputerDimension, BatteryDimension, SolarPanelDimension
import src.configs.config as config_file
from src.configs.output_enums import OutputFormat, OutputType
from src.configs.rate_enums import EmitRate, ErrorRate



def test_from_dict_when_only_required_config_is_provided():
    # Assign
    # Act
    config: Config = Config.from_dict(tests_config_val.REQUIRED_ONLY_CONFIG)

    # Assert
    assert config == tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG


def test_from_dict_when_full_config_provided():
    # Assign
    # Act
    config = Config.from_dict(tests_config_val.REQUIRED_AND_OPTIONAL_CONFIG)

    # Assert
    assert config == tests_config_val.EXPECTED_REQUIRED_AND_OPTIONAL_CONFIG


def test_from_dict_when_dimensions_is_an_complete_list():
    # Assign
    data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "dimensions": config_file.ALL_VALID_DIMENSIONS}

    # Act
    config = Config.from_dict(data)

    # Assert
    assert config == tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG

@pytest.mark.parametrize(
    "provided_list",
    [
        ["temperature"],
        ["temperature", "humidity"],
        ["temperature", "cpu-temperature", "current-amp"],
    ],
)
def test_from_dict_when_dimensions_is_an_incomplete_list(
    provided_list: list[str]
):
    # Assign
    data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "dimensions": provided_list}
    expected_result = copy.deepcopy(tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG)
    expected_result.dimensions.sensors.temperature.is_enabled = SensorDimension.TEMPERATURE.value in provided_list
    expected_result.dimensions.sensors.humidity.is_enabled = SensorDimension.HUMIDITY.value in provided_list
    expected_result.dimensions.sensors.co2.is_enabled = SensorDimension.CO2.value in provided_list
    expected_result.dimensions.sensors.ozone.is_enabled = SensorDimension.OZONE.value in provided_list
    expected_result.dimensions.sensors.nitrogen_dioxide.is_enabled = SensorDimension.NITROGEN_DIOXIDE.value in provided_list
    expected_result.dimensions.sensors.barometric_pressure.is_enabled = SensorDimension.BAROMETRIC_PRESSURE.value in provided_list
    expected_result.dimensions.sensors.solar_radiation.is_enabled = SensorDimension.SOLAR_RADIATION.value in provided_list
    expected_result.dimensions.sensors.salinity.is_enabled = SensorDimension.SALINITY.value in provided_list
    expected_result.dimensions.sensors.ph.is_enabled = SensorDimension.PH.value in provided_list
    expected_result.dimensions.sensors.plastics.is_enabled = SensorDimension.PLASTICS.value in provided_list
    
    expected_result.dimensions.computer.cpu_temperature.is_enabled = ComputerDimension.CPU_TEMPERATURE.value in provided_list
    expected_result.dimensions.computer.cpu_utilization.is_enabled = ComputerDimension.CPU_UTILIZATION.value in provided_list
    expected_result.dimensions.battery.battery_temperature.is_enabled = BatteryDimension.BATTERY_TEMPERATURE.value in provided_list
    expected_result.dimensions.battery.battery_percentage_level.is_enabled =  BatteryDimension.BATTERY_PERCENTAGE_LEVEL.value in provided_list
    expected_result.dimensions.solar_panel.current_voltage.is_enabled = SolarPanelDimension.CURRENT_VOLTAGE.value in provided_list
    expected_result.dimensions.solar_panel.current_amp.is_enabled = SolarPanelDimension.CURRENT_AMP.value in provided_list

    # Act
    config = Config.from_dict(data)

    # Assert
    assert config == expected_result


@pytest.mark.parametrize(
    "output_format, expected_value",
    [
        ["json", OutputFormat.JSON],
        ["xml", OutputFormat.XML],
        ["csv", OutputFormat.CSV],
        ["avro", OutputFormat.AVRO],
        ["json-with-binary-payload", OutputFormat.JSON_WITH_BINARY_PAYLOAD],
        ["xml-with-binary-payload", OutputFormat.XML_WITH_BINARY_PAYLOAD],
        ["csv-with-binary-payload", OutputFormat.CSV_WITH_BINARY_PAYLOAD],
        ["avro-with-binary-payload", OutputFormat.AVRO_WITH_BINARY_PAYLOAD],
    ],
)
def test_from_dict_when_valid_output_formats_are_provided(
    output_format: str,
    expected_value: OutputFormat,
):
    # Assign
    input_data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "output-format": output_format}
    expected_result = copy.deepcopy(tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG)
    expected_result.output_format = expected_value

    # Act
    config = Config.from_dict(input_data)

    # Assert
    assert config == expected_result


@pytest.mark.parametrize(
    "output_type, expected_value",
    [
        ["kafka-only", OutputType.KAFKA_ONLY],
        ["rabbitmq-only", OutputType.RABBITMQ_ONLY],
        ["s3-only", OutputType.S3_ONLY],
        ["s3-with-kafka", OutputType.S3_WITH_KAFKA],
        ["s3-with-rabbitmq", OutputType.S3_WITH_RABBITMQ],
    ],
)
def test_from_dict_when_valid_output_types_are_provided(
    output_type: str,
    expected_value: OutputType,
):
    # Assign
    input_data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "output-type": output_type}
    expected_result = copy.deepcopy(tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG)
    expected_result.output_type = expected_value

    # Act
    config = Config.from_dict(input_data)

    # Assert
    assert config == expected_result

@pytest.mark.parametrize(
    "rate_of_emitting, expected_value",
    [
        ["1-per-second", EmitRate.ONE_PER_SECOND],
        ["10-per-second", EmitRate.TEN_PER_SECOND],
        ["1-per-minute", EmitRate.ONE_PER_MINUTE],
        ["10-per-minute", EmitRate.TEN_PER_MINUTE],
        ["1-per-hour", EmitRate.ONE_PER_HOUR],
        ["10-per-hour", EmitRate.TEN_PER_HOUR]
    ],
)
def test_from_dict_when_valid_rate_of_emitting_dp_are_provided(
    rate_of_emitting: str,
    expected_value: EmitRate,
):
    # Assign
    input_data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "rate-of-emitting-dp": rate_of_emitting}
    expected_result = copy.deepcopy(tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG)
    expected_result.rate_of_emitting_dp = expected_value

    # Act
    config = Config.from_dict(input_data)

    # Assert
    assert config == expected_result


@pytest.mark.parametrize(
    "error_rate_value, expected_error_rate",
    [
        [0.0, ErrorRate.NONE],
        [0.1, ErrorRate.LOW],
        [0.25, ErrorRate.MEDIUM],
        [0.5, ErrorRate.HIGH],
        [0.75, ErrorRate.CRITICAL],
        [1.0, ErrorRate.CERTAIN],
    ],
)
def test_from_dict_when_valid_error_rate_values_are_provided(
    error_rate_value: float,
    expected_error_rate: ErrorRate,
):
    # Assign
    input_data = {**tests_config_val.REQUIRED_ONLY_CONFIG, "error-rate": {"sensors": {"temperature": error_rate_value}}}
    expected_result = copy.deepcopy(tests_config_val.EXPECTED_REQUIRED_ONLY_CONFIG)
    expected_result.dimensions.sensors.temperature.error_rate = expected_error_rate

    # Act
    config = Config.from_dict(input_data)

    # Assert
    assert config == expected_result
