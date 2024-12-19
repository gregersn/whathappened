from pathlib import Path

import pytest
import yaml

from whathappened.sheets.schema.base import CURRENT_SCHEMA_VERSION
from whathappened.sheets.schema.build import validate
from whathappened.sheets.schema.utils import find_system, find_version, migrate

expected_sheets = list(sorted(Path("tests/sheets/expected/").glob("*.yml")))


def load_sheet(filename: Path):
    with open(filename, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.mark.parametrize(
    "sheet",
    expected_sheets,
    ids=[str(sheet.name) for sheet in expected_sheets],
)
def test_migration(sheet: Path):
    assert sheet.is_file()
    original_data = load_sheet(sheet)
    data = migrate(original_data, CURRENT_SCHEMA_VERSION)
    assert not validate(data, find_system(data))

    assert original_data == migrate(data, find_version(original_data))
