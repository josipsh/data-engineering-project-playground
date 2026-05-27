import pytest

from src.configs.config_parameters_enums import ConfigParameters
from src.configs.config import Config
from src.errors.config_error import ConfigError

import tests.configs.value_consts as tests_config_val

@pytest.mark.parametrize(
    "missing_fields, expected_error",
    [
        [[ConfigParameters.OUTPUT_FORMAT], "While processing configuration the following errors occurred:\n- Missing required parameter: `output-format`"],
        [[ConfigParameters.OUTPUT_TYPE], "While processing configuration the following errors occurred:\n- Missing required parameter: `output-type`"],
        [[ConfigParameters.NUMBER_OF_DEVICES_PER_FLEET], "While processing configuration the following errors occurred:\n- Missing required parameter: `number-of-devices-per-fleet`"],
        [[ConfigParameters.NUMBER_OF_FLEETS], "While processing configuration the following errors occurred:\n- Missing required parameter: `number-of-fleets`"],
        [[ConfigParameters.DIMENSIONS], "While processing configuration the following errors occurred:\n- Missing required parameter: `dimensions`"],
        [[ConfigParameters.RATE_OF_EMITTING_DP], "While processing configuration the following errors occurred:\n- Missing required parameter: `rate-of-emitting-dp`"],
        [[ConfigParameters.OUTPUT_FORMAT, ConfigParameters.RATE_OF_EMITTING_DP], "While processing configuration the following errors occurred:\n- Missing required parameter: `output-format`\n- Missing required parameter: `rate-of-emitting-dp`"],
        [[ConfigParameters.OUTPUT_FORMAT, ConfigParameters.NUMBER_OF_DEVICES_PER_FLEET, ConfigParameters.RATE_OF_EMITTING_DP], "While processing configuration the following errors occurred:\n- Missing required parameter: `output-format`\n- Missing required parameter: `number-of-devices-per-fleet`\n- Missing required parameter: `rate-of-emitting-dp`"],
    ],
)
def test_from_dict_when_required_field_is_missing(
    missing_fields: list[ConfigParameters],
    expected_error: str,
):
    # Assign
    missing_fields = [x.value for x in missing_fields]
    data = {k: v for k, v in tests_config_val.REQUIRED_ONLY_CONFIG.items() if k not in missing_fields}
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict(data)

    # Assert
    assert str(caught_error.value) == expected_error

def test_from_dict_when_unknown_parameter_is_provided():
    # Assign
    data = {**tests_config_val.REQUIRED_ONLY_CONFIG, 'unsupported_parameter': 10}
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict(data)

    # Assert
    assert str(caught_error.value) == (
        "While processing configuration the following errors occurred:\n"
        "- Unsupported parameter was found, make sure there is no typos. Unsupported parameters: unsupported_parameter"
    )


# -------------------------------------------------------------------------------------------
# ------------------------ Invalid values ---------------------------------------------------
# -------------------------------------------------------------------------------------------
def test_from_dict_when_output_format_has_invalid_value():
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.OUTPUT_FORMAT.value: "unsupported_value"})

    # Assert
    assert str(caught_error.value) == (
        "While processing configuration the following errors occurred:\n"
        "- Invalid value for `output-format`: 'unsupported_value'. Expected one of: "
        "'json', 'xml', 'csv', 'avro', 'json-with-binary-payload', 'xml-with-binary-payload', 'csv-with-binary-payload', 'avro-with-binary-payload'"
    )

def test_from_dict_when_output_type_is_invalid():
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.OUTPUT_TYPE.value: "unsupported_value"})

    # Assert
    assert str(caught_error.value) == (
        "While processing configuration the following errors occurred:\n"
        "- Invalid value for `output-type`: 'unsupported_value'. Expected one of: "
        "'kafka-only', 'rabbitmq-only', 's3-only', 's3-with-kafka', 's3-with-rabbitmq'"
    )



@pytest.mark.parametrize(
    "input_value, expected_error",
    [
        [0, "While processing configuration the following errors occurred:\n- Invalid value for `number-of-devices-per-fleet`: 0. Expected a positive integer."],
        [-1, "While processing configuration the following errors occurred:\n- Invalid value for `number-of-devices-per-fleet`: -1. Expected a positive integer."],
        ["1", "While processing configuration the following errors occurred:\n- Invalid value for `number-of-devices-per-fleet`: '1'. Expected a positive integer."],
        ["one", "While processing configuration the following errors occurred:\n- Invalid value for `number-of-devices-per-fleet`: 'one'. Expected a positive integer."]
    ],
)
def test_from_dict_when_number_of_devices_per_fleet_has_invalid_value(
    input_value: int | str,
    expected_error: str
):
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.NUMBER_OF_DEVICES_PER_FLEET.value: input_value})

    # Assert
    assert str(caught_error.value) == expected_error

@pytest.mark.parametrize(
    "input_value, expected_error",
    [
        [0, "While processing configuration the following errors occurred:\n- Invalid value for `number-of-fleets`: 0. Expected a positive integer."],
        [-1, "While processing configuration the following errors occurred:\n- Invalid value for `number-of-fleets`: -1. Expected a positive integer."],
        ["1", "While processing configuration the following errors occurred:\n- Invalid value for `number-of-fleets`: '1'. Expected a positive integer."],
        ["one", "While processing configuration the following errors occurred:\n- Invalid value for `number-of-fleets`: 'one'. Expected a positive integer."]
    ],
)
def test_from_dict_when_number_of_fleets_has_invalid_value(
    input_value: int | str,
    expected_error: str
):
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.NUMBER_OF_FLEETS.value: input_value})

    # Assert
    assert str(caught_error.value) == expected_error


def test_from_dict_when_emit_rate_has_invalid_value():
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.RATE_OF_EMITTING_DP.value: "unsupported_rate"})

    # Assert
    assert str(caught_error.value) == (
        "While processing configuration the following errors occurred:\n"
        "- Invalid value for `rate-of-emitting-dp`: 'unsupported_rate'. Expected one of: "
        "'1-per-second', '10-per-second', '1-per-minute', '10-per-minute', '1-per-hour', '10-per-hour'"
    )

@pytest.mark.parametrize(
    "input_value, expected_error",
    [
        [["not-a-dimension"], "While processing configuration the following errors occurred:\n- Invalid value for `dimensions` parameter.\nInvalid dimensions are: not-a-dimension\nExpected 'all' or a non-empty list of dimension strings. The valid dimensions are `temperature, humidity, co2, ozone, nitrogen-dioxide, barometric-pressure, solar-radiation, salinity, ph, plastics, battery-temperature, battery-percentage-level, current-voltage, current-amp, cpu-temperature, cpu-utilization`"],
        [[], "While processing configuration the following errors occurred:\n- Invalid value for `dimensions` parameter.\nReceived value is an empty list.\nExpected 'all' or a non-empty list of dimension strings. The valid dimensions are `temperature, humidity, co2, ozone, nitrogen-dioxide, barometric-pressure, solar-radiation, salinity, ph, plastics, battery-temperature, battery-percentage-level, current-voltage, current-amp, cpu-temperature, cpu-utilization`"],
    ],
)
def test_from_dict_when_dimensions_has_invalid_value(
    input_value: list[int | str],
    expected_error: str
):
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, ConfigParameters.DIMENSIONS.value: input_value})

    # Assert
    assert str(caught_error.value) == expected_error

@pytest.mark.parametrize(
    "input_value, expected_error",
    [
        [ # has value has unsupported component
            {"unsupported_component": {"temperature": 0.1}},
            (
                "While processing configuration the following errors occurred:\n"
                "- Unknown component `unsupported_component` occurred in `error-rate` parameter. "
                "Valid components are: sensors, computer, battery, solar-panel"
            )
        ],
        [ # has value has unsupported dimension in valid component
            {"sensors": {"unsupported_dimension": 0.1}},
            (
                "While processing configuration the following errors occurred:\n"
                "- Dimension in the component `sensors` is invalid. Received dimension is `unsupported_dimension`. Valid dimensions for component `sensors` are `temperature, humidity, co2, ozone, nitrogen-dioxide, barometric-pressure, solar-radiation, salinity, ph, plastics`"
            )
        ],
        [ # has not supported float value for given dimension in given component
            {"sensors": {"temperature": 0.33}},
            (
                "While processing configuration the following errors occurred:\n- A value `0.33` for the dimension `temperature` "
                "in the component `sensors` is invalid. Valid values are: 0.0, 0.1, 0.25, 0.5, 0.75, 1.0"
            )
        ],
        [ # has string value for component instead dict
            {"sensors": "not-a-dict"},
            (
                "While processing configuration the following errors occurred:\n- Invalid value component sensors. "
                "We expect a `dict`, but we got `str`. An expected value is dict with components and dimensions, "
                'e.g. {"sensors": "temperature": 0.1}'
            )
        ],
        [ # has string value for parameter instead dict
            'invalid_error_rate',
            (
                "While processing configuration the following errors occurred:\n- Invalid value for `error-rate`: we have got `invalid_error_rate`. "
                'An expected value is dict with components and dimensions, e.g. {"sensors": "temperature": 0.1}'
            )
        ],
    ],
)
def test_from_dict_when_value_for_error_rate_parameter_is_invalid(
    input_value: dict | str,
    expected_error: str
):
    # Assign
    with pytest.raises(ConfigError) as caught_error:
        # Act
        Config.from_dict({**tests_config_val.REQUIRED_ONLY_CONFIG, "error-rate": input_value})

    # Assert
    assert str(caught_error.value) == expected_error
