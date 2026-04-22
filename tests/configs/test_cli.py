import pytest

import src.configs.cli as cli
from src.configs.cli import CliParsedArgs


@pytest.mark.parametrize(
    "input_args, expected_config_filepath, expected_config_validation",
    [
        [ # required flag before optional flag
            ["--config", "config/sample.yaml", "--validate-config"],
            "config/sample.yaml",
            True
        ],
        [ # optional flag before required flag
            ["--validate-config", "--config", "config/sample.yaml"],
            "config/sample.yaml",
            True
        ],
        [ # only required flag provided
            ["--config", "config/sample.yaml"],
            "config/sample.yaml",
            False
        ],
    ],
)
def test_parse_args_when_valid_flags_are_provided(
    input_args: list[str],
    expected_config_filepath: str,
    expected_config_validation: bool,
):
    # Assign
    # Act
    args: CliParsedArgs = cli.parse_args(input_args)

    # Assert
    assert args.config_filepath == expected_config_filepath
    assert args.is_validate_config_enabled is expected_config_validation


def test_parse_args_when_required_flags_are_missing():
    # Assign
    with pytest.raises(SystemExit) as caught_error:
        # Act
        cli.parse_args([])

    # Assert
    assert caught_error.value.code == 2
