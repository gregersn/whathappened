from pathlib import Path
import yaml
import pytest

from tests.sheets.utils import write_yaml
from whathappened.sheets.schema.base import BaseSheet


def test_base_schema():
    current_schema = BaseSheet.model_json_schema(mode="serialization")
    assert current_schema

    expected_file = Path("tests/schemas/expected/base.yml")
    current_file = Path("tests/schemas/current/base.yml")

    if not expected_file.is_file():
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(current_schema, expected_file)
        assert False, "No expected schema, wrote one to file."

    with open(expected_file, "r", encoding="utf8") as f:
        expected_schema = yaml.safe_load(f)

    if not current_schema == expected_schema:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(current_schema, f, sort_keys=True)
        assert current_schema == expected_schema
