"""Schema and sheet utilities"""

import copy
from packaging.version import Version, parse

SheetVersion = Version


def up_or_down(from_version: SheetVersion, to_version: SheetVersion) -> int:
    """Deteremine if migration is up or down."""
    if from_version > to_version:
        return -1

    if to_version > from_version:
        return 1

    return 0


def find_migration(version: SheetVersion, direction: int, migrations):
    """Find migration function."""
    for m in migrations:
        if direction > 0 and parse(m["from"]) == version:
            return m

        if direction < 0 and parse(m["to"]) == version:
            return m
    return None


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


def migrate(data, to_version, migrations=None):
    """Do the migration."""
    data = copy.deepcopy(data)
    from_version = parse(find_version(data))
    direction = up_or_down(from_version, parse(to_version))
    if direction == 0:
        return data

    migrator = find_migration(from_version, direction, migrations)

    if migrator is None:
        raise NotImplementedError("Migrator not found")

    if direction < 0:
        data = migrator["down"](data)

    if direction > 0:
        data = migrator["up"](data)

    return migrate(data, to_version=to_version, migrations=migrations)
