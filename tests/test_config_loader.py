import os
import tempfile

import pytest

from config_loader import load_config

VALID_YAML = """\
output-format: json
output-type: kafka-only
number-of-devices-per-fleet: 50
number-of-fleets: 5
dimensions: all
rate-of-emitting-dp: 10-per-second
"""


def test_load_valid_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        config = load_config(path)
        assert config.output_format.value == "json"
        assert config.number_of_devices_per_fleet == 50
        assert config.error_rate is None
    finally:
        os.unlink(path)


def test_load_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_load_unreadable_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(VALID_YAML)
        path = f.name
    try:
        os.chmod(path, 0o000)
        with pytest.raises(PermissionError):
            load_config(path)
    finally:
        os.chmod(path, 0o644)
        os.unlink(path)


def test_load_invalid_content_raises_value_error():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("output-format: not-a-format\n")
        path = f.name
    try:
        with pytest.raises(ValueError):
            load_config(path)
    finally:
        os.unlink(path)


def test_load_file_with_error_rate():
    yaml_content = VALID_YAML + "error-rate:\n  antenna: 0.5\n"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        path = f.name
    try:
        config = load_config(path)
        from config import ErrorRate
        assert config.error_rate["antenna"] == ErrorRate.HIGH
    finally:
        os.unlink(path)
