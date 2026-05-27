from typing import Any

import yaml

from src.errors.yaml_error import YamlError


def load(path: str) -> dict[str, Any]:
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError as ex:
        raise YamlError(f"File `{path}` does not exist") from ex
    except Exception as ex:
        raise YamlError(f"Unable to read File `{path}`.") from ex
