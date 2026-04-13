import pytest

from cli import parse_args


def test_parse_config_path():
    args = parse_args(["--config", "config/sample.yaml"])
    assert args.config == "config/sample.yaml"


def test_validate_config_flag_absent_by_default():
    args = parse_args(["--config", "config/sample.yaml"])
    assert args.validate_config is False


def test_validate_config_flag_present():
    args = parse_args(["--config", "config/sample.yaml", "--validate-config"])
    assert args.validate_config is True


def test_missing_config_arg_exits_nonzero():
    with pytest.raises(SystemExit) as exc_info:
        parse_args([])
    assert exc_info.value.code != 0


def test_validate_config_before_config_arg():
    args = parse_args(["--validate-config", "--config", "config/sample.yaml"])
    assert args.config == "config/sample.yaml"
    assert args.validate_config is True
