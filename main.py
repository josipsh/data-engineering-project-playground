import sys

import yaml

import src.configs.cli as cli
import src.utils.yaml_loader as yaml_loader
from src.configs.cli import CliParsedArgs
from src.configs.config import Config
from src.generator.data_generator import DataGenerator
from src.generator.models import DeviceOutput


def _print_to_stdout(outputs: list[DeviceOutput]) -> None:
    for device_output in outputs:
        print(device_output.device_id)
        for record in device_output.records:
            print(f"{record.record_number} - {record.battery} | {record.temperature}")
        print("-----------")


def main() -> None:
    try:
        cli_args: CliParsedArgs = cli.parse_args(sys.argv[1:])

        loaded_config = yaml_loader.load(cli_args.config_filepath)
        parsed_config = Config.from_dict(loaded_config)

        if cli_args.is_validate_config_enabled:
            config_dict = parsed_config.to_dict()
            print(yaml.dump(config_dict))
            return

        if cli_args.is_stdout_enabled:
            outputs = DataGenerator(parsed_config).generate()
            _print_to_stdout(outputs)
            return

        print("Executing started....")
    except Exception as e:
        print(f"Error: invalid config:\n{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
