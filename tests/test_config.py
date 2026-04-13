import pytest

from config import (
    BatteryDimensions,
    ComputerDimensions,
    Config,
    EmitRate,
    ErrorRate,
    OutputFormat,
    OutputType,
    SensorsDimensions,
    SolarPanelDimensions,
)

VALID_MINIMAL = {
    "output-format": "json",
    "output-type": "kafka-only",
    "number-of-devices-per-fleet": 50,
    "number-of-fleets": 5,
    "dimensions": "all",
    "rate-of-emitting-dp": "10-per-second",
}

VALID_FULL = {
    **VALID_MINIMAL,
    "error-rate": {
        "sensors": {"temperature": 0.1, "humidity": 0.25},
        "antenna": 0.5,
    },
}


# --- Valid inputs ---

def test_from_dict_valid_minimal():
    config = Config.from_dict(VALID_MINIMAL)
    assert config.output_format == OutputFormat.JSON
    assert config.output_type == OutputType.KAFKA_ONLY
    assert config.number_of_devices_per_fleet == 50
    assert config.number_of_fleets == 5
    assert config.dimensions == "all"
    assert config.rate_of_emitting_dp == EmitRate.TEN_PER_SECOND
    assert config.error_rate is None


def test_from_dict_valid_full_error_rate():
    config = Config.from_dict(VALID_FULL)
    assert config.error_rate["sensors"]["temperature"] == ErrorRate.LOW
    assert config.error_rate["sensors"]["humidity"] == ErrorRate.MEDIUM
    assert config.error_rate["antenna"] == ErrorRate.HIGH


def test_from_dict_dimensions_list():
    data = {**VALID_MINIMAL, "dimensions": ["temperature", "humidity", "cpu_temperature"]}
    config = Config.from_dict(data)
    assert SensorsDimensions.TEMPERATURE in config.dimensions
    assert SensorsDimensions.HUMIDITY in config.dimensions
    assert ComputerDimensions.CPU_TEMPERATURE in config.dimensions


def test_from_dict_all_output_formats():
    valid_formats = [
        "json", "json-with-binary-payload", "xml", "xml-with-binary-payload",
        "csv", "csv-with-binary-payload", "avro", "avro_with_binary_payload",
    ]
    for fmt in valid_formats:
        config = Config.from_dict({**VALID_MINIMAL, "output-format": fmt})
        assert config.output_format.value == fmt


def test_from_dict_all_output_types():
    valid_types = ["kafka-only", "rabbitmq-only", "s3-only", "s3-with-kafka", "s3-with-rabbitmq"]
    for ot in valid_types:
        config = Config.from_dict({**VALID_MINIMAL, "output-type": ot})
        assert config.output_type.value == ot


def test_from_dict_error_rate_none_string():
    config = Config.from_dict({**VALID_MINIMAL, "error-rate": "none"})
    assert config.error_rate is None


def test_from_dict_error_rate_omitted():
    config = Config.from_dict(VALID_MINIMAL)
    assert config.error_rate is None


def test_from_dict_error_rate_all_components():
    data = {
        **VALID_MINIMAL,
        "error-rate": {
            "sensors": {"temperature": 0.1},
            "computer": {"cpu_utilization": 0.25},
            "battery": {"battery_temperature": 0.5},
            "solar_panel": {"current_voltage": 0.75},
            "antenna": 1.0,
        },
    }
    config = Config.from_dict(data)
    assert config.error_rate["sensors"]["temperature"] == ErrorRate.LOW
    assert config.error_rate["computer"]["cpu_utilization"] == ErrorRate.MEDIUM
    assert config.error_rate["battery"]["battery_temperature"] == ErrorRate.HIGH
    assert config.error_rate["solar_panel"]["current_voltage"] == ErrorRate.CRITICAL
    assert config.error_rate["antenna"] == ErrorRate.CERTAIN


def test_from_dict_all_error_rate_values():
    for val in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]:
        data = {**VALID_MINIMAL, "error-rate": {"antenna": val}}
        config = Config.from_dict(data)
        assert config.error_rate["antenna"].value == val


# --- Missing required parameters ---

def test_missing_output_format():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "output-format"}
    with pytest.raises(ValueError, match="output-format"):
        Config.from_dict(data)


def test_missing_output_type():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "output-type"}
    with pytest.raises(ValueError, match="output-type"):
        Config.from_dict(data)


def test_missing_number_of_devices_per_fleet():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "number-of-devices-per-fleet"}
    with pytest.raises(ValueError, match="number-of-devices-per-fleet"):
        Config.from_dict(data)


def test_missing_number_of_fleets():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "number-of-fleets"}
    with pytest.raises(ValueError, match="number-of-fleets"):
        Config.from_dict(data)


def test_missing_dimensions():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "dimensions"}
    with pytest.raises(ValueError, match="dimensions"):
        Config.from_dict(data)


def test_missing_rate_of_emitting_dp():
    data = {k: v for k, v in VALID_MINIMAL.items() if k != "rate-of-emitting-dp"}
    with pytest.raises(ValueError, match="rate-of-emitting-dp"):
        Config.from_dict(data)


def test_multiple_errors_reported_at_once():
    with pytest.raises(ValueError) as exc_info:
        Config.from_dict({})
    msg = str(exc_info.value)
    assert "output-format" in msg
    assert "output-type" in msg
    assert "dimensions" in msg
    assert "rate-of-emitting-dp" in msg


# --- Invalid values ---

def test_invalid_output_format():
    with pytest.raises(ValueError, match="output-format"):
        Config.from_dict({**VALID_MINIMAL, "output-format": "not-a-format"})


def test_invalid_output_type():
    with pytest.raises(ValueError, match="output-type"):
        Config.from_dict({**VALID_MINIMAL, "output-type": "not-a-type"})


def test_invalid_number_zero():
    with pytest.raises(ValueError, match="number-of-devices-per-fleet"):
        Config.from_dict({**VALID_MINIMAL, "number-of-devices-per-fleet": 0})


def test_invalid_number_negative():
    with pytest.raises(ValueError, match="number-of-fleets"):
        Config.from_dict({**VALID_MINIMAL, "number-of-fleets": -1})


def test_invalid_number_string():
    with pytest.raises(ValueError, match="number-of-devices-per-fleet"):
        Config.from_dict({**VALID_MINIMAL, "number-of-devices-per-fleet": "fifty"})


def test_invalid_dimensions_unknown():
    with pytest.raises(ValueError, match="dimensions"):
        Config.from_dict({**VALID_MINIMAL, "dimensions": ["not-a-dimension"]})


def test_invalid_dimensions_empty_list():
    with pytest.raises(ValueError, match="dimensions"):
        Config.from_dict({**VALID_MINIMAL, "dimensions": []})


def test_invalid_rate_of_emitting():
    with pytest.raises(ValueError, match="rate-of-emitting-dp"):
        Config.from_dict({**VALID_MINIMAL, "rate-of-emitting-dp": "5-per-second"})


def test_invalid_error_rate_unknown_component():
    with pytest.raises(ValueError, match="error-rate"):
        Config.from_dict({**VALID_MINIMAL, "error-rate": {"bad_component": {"temperature": 0.1}}})


def test_invalid_error_rate_unknown_dimension():
    with pytest.raises(ValueError, match="error-rate"):
        Config.from_dict({**VALID_MINIMAL, "error-rate": {"sensors": {"bad_dim": 0.1}}})


def test_invalid_error_rate_bad_float():
    with pytest.raises(ValueError, match="error-rate"):
        Config.from_dict({**VALID_MINIMAL, "error-rate": {"sensors": {"temperature": 0.33}}})


def test_invalid_error_rate_antenna_sub_dict():
    with pytest.raises(ValueError, match="error-rate"):
        Config.from_dict({**VALID_MINIMAL, "error-rate": {"antenna": {"bad": 0.1}}})


def test_invalid_error_rate_not_a_mapping():
    with pytest.raises(ValueError, match="error-rate"):
        Config.from_dict({**VALID_MINIMAL, "error-rate": "bad"})


# --- __str__ output ---

def test_str_all_dimensions_no_error_rate():
    config = Config.from_dict(VALID_MINIMAL)
    s = str(config)
    assert "output-format: json" in s
    assert "output-type: kafka-only" in s
    assert "number-of-devices-per-fleet: 50" in s
    assert "number-of-fleets: 5" in s
    assert "dimensions: all" in s
    assert "rate-of-emitting-dp: 10-per-second" in s
    assert "error-rate: none" in s


def test_str_with_error_rate():
    config = Config.from_dict(VALID_FULL)
    s = str(config)
    assert "sensors.temperature=low" in s
    assert "sensors.humidity=medium" in s
    assert "antenna=high" in s


def test_str_dimensions_list_sorted():
    data = {**VALID_MINIMAL, "dimensions": ["humidity", "temperature"]}
    config = Config.from_dict(data)
    s = str(config)
    assert "dimensions: humidity, temperature" in s
