import sys

import yaml

import src.configs.cli as cli
import src.utils.yaml_loader as yaml_loader
from src.configs.cli import CliParsedArgs
from src.configs.config import Config


def main() -> None:
    try:
        cli_args: CliParsedArgs = cli.parse_args(sys.argv[1:])

        loaded_config = yaml_loader.load(cli_args.config_filepath)
        parsed_config = Config.from_dict(loaded_config)

        if cli_args.is_validate_config_enabled:
            config_dict = parsed_config.to_dict()
            print(yaml.dump(config_dict))
            return

        print("Executing started....")
    except Exception as e:
        print(f"Error: invalid config:\n{e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
