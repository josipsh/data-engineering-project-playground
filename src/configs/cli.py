import argparse
from dataclasses import dataclass


@dataclass
class CliParsedArgs: 
    config_filepath: str
    is_validate_config_enabled: bool

def parse_args(argv: list[str]) -> CliParsedArgs:
    parser = argparse.ArgumentParser(
        description="Mock data generator for ocean-deployed sensor devices"
    )
    parser.add_argument(
        "--config",
        required=True,
        metavar="PATH",
        help="Path to the YAML configuration file",
    )
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate the config file, print it, and exit",
    )
    namespace = parser.parse_args(argv)
    return CliParsedArgs(
        config_filepath=namespace.config,
        is_validate_config_enabled=namespace.validate_config,
    )
