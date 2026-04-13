import sys

from cli import parse_args
from config_loader import load_config


def main() -> None:
    args = parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: config file not found: {e.filename}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: could not read config file: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: invalid config:\n{e}", file=sys.stderr)
        sys.exit(1)

    if args.validate_config:
        print(config)
        sys.exit(0)

    print("Executing started....")
    sys.exit(0)


if __name__ == "__main__":
    main()
