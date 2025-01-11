from pathlib import Path
import pytest
from packaging.version import parse

from whathappened.core.sheets.schema.utils import (
    migrate,
    up_or_down,
    find_migration,
    find_version,
    Migration,
)

BASEDIR = Path(__file__).parent.absolute()


def test_up_or_down():
    assert up_or_down(parse("1.0.0"), parse("1.0.0")) == 0
    assert up_or_down(parse("1.0.0"), parse("1.0.1")) == 1
    assert up_or_down(parse("1.0.1"), parse("1.0.0")) == -1


def test_find_migration():
    assert find_migration(parse("2.0.0"), 1, migrations) is None
    assert find_migration(parse("1.0.1"), 1, migrations) == migrations[2]
    assert find_migration(parse("1.0.1"), -1, migrations) == migrations[1]


def test_find_version():
    assert find_version({"version": "1.2.3"}) == "1.2.3"
    assert find_version({"meta": {"Version": "2.3.4"}}) == "2.3.4"
    assert find_version({}) == "0.0.0"


def test_migrate_same():
    data = {"meta": {"Version": "1.0.0"}}

    migrated = migrate(data, "1.0.0", [])

    assert migrated == data


def v1_0_0_to_v1_0_1(data):
    new_schema = data.copy()
    data["meta"]["Version"] = "1.0.1"
    return new_schema


def v1_0_1_to_v1_0_0(data):
    new_schema = data.copy()
    data["meta"]["Version"] = "1.0.0"
    return new_schema


migrations = [
    Migration("0.9", "1.0.0"),
    Migration(
        "1.0.0",
        "1.0.1",
        v1_0_0_to_v1_0_1,
        v1_0_1_to_v1_0_0,
    ),
    Migration("1.0.1", "1.0.2"),
]


def test_migrate_up():
    data = {"meta": {"Version": "1.0.0"}}

    migrated = migrate(data, "1.0.1", migrations=migrations)

    assert migrated["meta"]["Version"] == "1.0.1"


def test_migrate_unavailable():
    data = {"version": "1.0.2"}
    with pytest.raises(Exception):
        migrate(data, "2.0.0", migrations=migrations)


def test_migrate_down():
    data = {"meta": {"Version": "1.0.1"}}

    migrated = migrate(data, "1.0.0", migrations=migrations)

    assert migrated["meta"]["Version"] == "1.0.0"
