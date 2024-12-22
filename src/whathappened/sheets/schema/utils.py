"""Schema and sheet utilities"""

import copy
from typing import Optional
from packaging.version import Version, parse

from whathappened.sheets.schema.base import (
    Migration,
    Gametag,
    migrations as base_migrations,
)

SheetVersion = Version


def up_or_down(from_version: SheetVersion, to_version: SheetVersion) -> int:
    """Deteremine if migration is up or down."""
    if from_version > to_version:
        return -1

    if to_version > from_version:
        return 1

    return 0


def find_migration(version: SheetVersion, direction: int, migrations: list[Migration]):
    """Find migration function."""
    for m in migrations:
        if direction > 0 and parse(m.from_version) == version:
            return m

        if direction < 0 and parse(m.to) == version:
            return m


def find_version(data) -> str:
    """Find version string in schema."""
    version_string = None

    try:
        version_string = data["version"]
        return version_string
    except KeyError:
        pass

    try:
        version_string = data["meta"]["Version"]
        return version_string
    except KeyError:
        pass

    return "0.0.0"


def find_system(data):
    """Find the game system for the sheet."""
    system = data.get("system", "coc7e")

    return system


def find_migrations(system: Gametag) -> list[Migration]:
    system_migrations = []
    try:
        import importlib

        game_module = importlib.import_module(f"whathappened.sheets.schema.{system}")
        if hasattr(game_module, "migrations"):
            system_migrations = game_module.migrations
    except ImportError:
        pass
    except AttributeError:
        pass

    return system_migrations + base_migrations


def set_version(data, version: str):
    data = data.copy()
    data["version"] = version
    return data


def migrate(data, to_version: str, migrations: Optional[list[Migration]] = None):
    """Do the migration."""
    data = copy.deepcopy(data)
    system = find_system(data)
    if migrations is None:
        migrations = find_migrations(system)
    assert system
    from_version = parse(find_version(data))
    direction = up_or_down(from_version, parse(to_version))
    if direction == 0:
        return data

    migrator = find_migration(from_version, direction, migrations)

    if migrator is None:
        raise NotImplementedError(
            f"Migrator not found for {system} from {from_version} to {to_version}"
        )

    if direction < 0:
        if migrator.down:
            data = migrator.down(data)
        else:
            data = set_version(data, to_version)

    if direction > 0:
        if migrator.up:
            data = migrator.up(data)
        else:
            data = set_version(data, to_version)

    return migrate(data, to_version=to_version, migrations=migrations)
