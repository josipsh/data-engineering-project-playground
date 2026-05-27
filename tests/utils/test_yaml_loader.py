import os
import tempfile

import pytest

from src.errors.yaml_error import YamlError
import src.utils.yaml_loader as yaml_loader

VALID_YAML = """\
output-format: json
output-type: kafka-only
number-of-devices-per-fleet: 50
number-of-fleets: 5
dimensions: all
rate-of-emitting-dp: 10-per-second
"""

EXPECTED_RESULT = {
    "output-format": "json",
    "output-type": "kafka-only",
    "number-of-devices-per-fleet": 50,
    "number-of-fleets": 5,
    "dimensions": "all",
    "rate-of-emitting-dp": "10-per-second"
}


def test_load_when_valid_yaml_file_is_provided():
    # Assign
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
        f.write(VALID_YAML)
        f.flush()

        # Act
        result = yaml_loader.load(f.name)

    # Assert
    assert result == EXPECTED_RESULT


def test_load_when_file_does_not_exist():
    # Assign
    with pytest.raises(YamlError) as caught_error:
        # Act
        yaml_loader.load("/nonexistent/path/config.yaml")

    # Assert
    assert str(caught_error.value) == "File `/nonexistent/path/config.yaml` does not exist"


def test_load_when_file_is_not_readable():
    # Assign
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
        f.write(VALID_YAML)
        f.flush()
        os.chmod(f.name, 0o000)
        path = f.name

        with pytest.raises(YamlError) as caught_error:
            # Act
            yaml_loader.load(f.name)

        os.chmod(f.name, 0o644)  # restore so NamedTemporaryFile can delete it on exit

    # Assert
    assert str(caught_error.value) == f"Unable to read File `{path}`."


def test_load_when_file_has_invalid_yaml_syntax():
    # Assign
    invalid_yaml = "invalid: [unbalanced bracket\nkey: value"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as f:
        f.write(invalid_yaml)
        f.flush()
        path = f.name

        with pytest.raises(YamlError) as caught_error:
            # Act
            yaml_loader.load(f.name)

    # Assert
    assert str(caught_error.value) == f"Unable to read File `{path}`."

