import yaml
from config import Config


def load_config(path: str) -> Config:
    with open(path) as f:
        data = yaml.safe_load(f)
    return Config.from_dict(data)
