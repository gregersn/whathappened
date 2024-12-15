from pathlib import Path

import yaml


def write_yaml(data, filename: Path):
    with open(filename, "w", encoding="utf8") as f:
        yaml.safe_dump(data, f, sort_keys=True)
