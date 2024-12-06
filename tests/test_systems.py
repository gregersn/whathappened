from typing import Literal
import typing
import pytest
import yaml
from pathlib import Path

from whathappened import sheets
from whathappened.sheets.schema.build import get_schema
from whathappened.sheets.utils import create_sheet

System = Literal["landf", "dod", "tftl", "coc7e", "vaesen"]
SYSTEMS: list[str] = list(typing.get_args(System))


@pytest.fixture
def sheet(system: System):
    return create_sheet(system)


def write_yaml(data, filename: Path):
    with open(filename, "w", encoding="utf8") as f:
        yaml.safe_dump(data, f, sort_keys=False)


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

    if not current_schema == expected_schema:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(current_schema, f, sort_keys=False)
        assert current_schema == expected_schema


@pytest.mark.parametrize("game", SYSTEMS)
def test_create_sheet(game: System):
    character_module = sheets.find_system(game)

    assert character_module

    test_sheet = character_module.new_character(
        "Test character", system=game, timestamp=1733213970
    )
    assert test_sheet

    expected_file = Path(f"tests/sheets/expected/{game}.yml")
    current_file = Path(f"tests/sheets/current/{game}.yml")

    if not expected_file.is_file():
        expected_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(test_sheet, expected_file)
        assert False, "No expected sheet, wrote one to file."

    with open(expected_file, "r", encoding="utf8") as f:
        expected_sheet = yaml.safe_load(f)

    if not test_sheet == expected_sheet:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(test_sheet, f, sort_keys=False)
        assert test_sheet == expected_sheet
