import typing
import pytest
import yaml
from pathlib import Path

from pytest_dependency import depends

from whathappened import sheets
from whathappened.core.sheets.schema.base import Gametag
from whathappened.core.sheets.schema.build import get_schema, flatten_schema, validate
from whathappened.core.sheets.schema.utils import find_version
from whathappened.core.sheets.utils import create_sheet


SYSTEMS: list[str] = list(typing.get_args(Gametag))


@pytest.fixture
def sheet(system: Gametag):
    return create_sheet(system)


def write_yaml(data, filename: Path):
    with open(filename, "w", encoding="utf8") as f:
        yaml.safe_dump(data, f, sort_keys=True)


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_expected_schema(request, game: Gametag):
    """Checks to see if we expect a schema."""
    current_schema = get_schema(game)
    assert current_schema

    expected_file = Path(f"tests/games/schemas/expected/{game}.yml")
    current_file = Path(f"tests/games/schemas/current/{game}.yml")

    if not expected_file.is_file():
        current_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(current_schema, current_file)
        assert False, "No expected schema, wrote one to file."


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_flattened_schemas(request, game: Gametag):
    """Checks that the current schema is similar-ish to the expected."""

    depends(request, [f"test_expected_schema[{game}]"])
    current_schema = get_schema(game)
    assert current_schema

    expected_file = Path(f"tests/games/schemas/expected/{game}.yml")
    current_file = Path(f"tests/games/schemas/current/{game}.yml")

    with open(expected_file, "r", encoding="utf8") as f:
        expected_schema = yaml.safe_load(f)

    flat_current = flatten_schema(current_schema)
    flat_expected = flatten_schema(expected_schema)

    if "$defs" in flat_current:
        del flat_current["$defs"]

    if "$defs" in flat_expected:
        del flat_expected["$defs"]

    if flat_current != flat_expected:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(current_schema, f, sort_keys=True)
        assert flat_current == flat_expected


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_written_schemas(request, game: Gametag):
    """Checks that the current schema is idnetical to the expected."""

    depends(request, [f"test_flattened_schemas[{game}]"])

    current_schema = get_schema(game)
    assert current_schema

    expected_file = Path(f"tests/games/schemas/expected/{game}.yml")
    current_file = Path(f"tests/games/schemas/current/{game}.yml")

    with open(expected_file, "r", encoding="utf8") as f:
        expected_schema = yaml.safe_load(f)

    if not current_schema == expected_schema:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(current_schema, f, sort_keys=True)
        assert current_schema == expected_schema


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_expected_sheet(request, game: Gametag):
    character_module = sheets.find_system(game)

    assert character_module

    test_sheet = character_module.new_character(
        "Test character", system=game, timestamp=1733213970
    )
    assert test_sheet

    version = find_version(test_sheet)
    assert version

    expected_file = Path(f"tests/games/sheets/expected/{game}-{version}.yml")
    current_file = Path(f"tests/games/sheets/current/{game}-{version}.yml")

    if not expected_file.is_file():
        current_file.parent.mkdir(parents=True, exist_ok=True)
        write_yaml(test_sheet, current_file)
        assert False, "No expected sheet, wrote one to file."


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_validate_sheet(request, game: Gametag):
    depends(request, [f"test_expected_sheet[{game}]"])

    character_module = sheets.find_system(game)
    test_sheet = character_module.new_character(
        "Test character", system=game, timestamp=1733213970
    )

    assert not validate(test_sheet, game)


@pytest.mark.parametrize("game", SYSTEMS)
@pytest.mark.dependency()
def test_create_sheet(request, game: Gametag):
    depends(request, [f"test_validate_sheet[{game}]"])

    character_module = sheets.find_system(game)

    test_sheet = character_module.new_character(
        "Test character", system=game, timestamp=1733213970
    )

    version = find_version(test_sheet)
    assert version

    expected_file = Path(f"tests/games/sheets/expected/{game}-{version}.yml")
    current_file = Path(f"tests/games/sheets/current/{game}-{version}.yml")

    with open(expected_file, "r", encoding="utf8") as f:
        expected_sheet = yaml.safe_load(f)

    if not test_sheet == expected_sheet:
        current_file.parent.mkdir(parents=True, exist_ok=True)
        with open(current_file, "w", encoding="utf8") as f:
            yaml.safe_dump(test_sheet, f, sort_keys=True)
        assert test_sheet == expected_sheet
