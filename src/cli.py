import argparse


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
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
    return parser.parse_args(argv)
