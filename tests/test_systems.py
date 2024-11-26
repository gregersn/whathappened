from typing import Literal
import typing
import pytest
import yaml
from pathlib import Path

from whathappened.sheets.schema.build import get_schema
from whathappened.sheets.utils import create_sheet

System = Literal["landf", "dod", "tftl"]
SYSTEMS: list[str] = list(typing.get_args(System))


@pytest.fixture
def sheet(system: System):
    return create_sheet(system)


def write_yaml(data, filename: Path):
    with open(filename, "w", encoding="utf8") as f:
        yaml.safe_dump(data, f)


@pytest.mark.parametrize("game", SYSTEMS)
def test_schemas(game: str):
    current_schema = get_schema(game)
    assert current_schema

    expected_file = Path(f"tests/schemas/expected/{game}.yml")
    current_file = Path(f"tests/schemas/current/{game}.yml")

    if not expected_file.is_file():
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(current_schema, expected_file)
        assert False, "No expected schema, wrote one to file."

    with open(expected_file, "r", encoding="utf8") as f:
        expected_schema = yaml.safe_load(f)

    if not expected_schema == current_schema:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(current_schema, f)
        assert expected_schema == current_schema


@pytest.mark.parametrize("game", SYSTEMS)
def test_create_sheet(game: str):
    sheet = create_sheet(game)
    assert sheet

    expected_file = Path(f"tests/sheets/expected/{game}.yml")
    current_file = Path(f"tests/sheets/current/{game}.yml")

    if not expected_file.is_file():
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(sheet, expected_file)
        assert False, "No expected sheet, wrote one to file."

    with open(expected_file, "r", encoding="utf8") as f:
        expected_sheet = yaml.safe_load(f)

    if not expected_sheet == sheet:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(sheet, f)
        assert expected_sheet == sheet